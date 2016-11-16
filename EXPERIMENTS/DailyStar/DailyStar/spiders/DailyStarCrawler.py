import scrapy
import logging
import datetime

from DailyStar.items import DailyStarItem
from newspaper import Article

from DailyStar.Helpers.CustomNERTagger import Tagger

#indico API_KEY 8ee6432e7dc137740c40c0af8d7e9d05

# Change these paths according to your system
STANFORD_NER_PATH = 'C:\StanfordParser\stanford-ner-2015-12-09\stanford-ner.jar'
STANFORD_CLASSIFIER_PATH = 'C:\StanfordParser\stanford-ner-2015-12-09\classifiers\english.all.3class.distsim.crf.ser.gz'

# Using elasticsearch
from elasticsearch import Elasticsearch

es = Elasticsearch()

class DailyStarSpider(scrapy.Spider):
    name = 'dailystar'

    def increase_day_by_one(self, d):
        d += datetime.timedelta(days=1)
        return d

    # def __init__(self, start_day, start_month, start_year):
    #     self.start_day = int(start_day)
    #     self.start_month = int(start_month)
    #     self.start_year = int(start_year)

    def start_requests(self):
        self.start_year = 2016
        self.start_month = 1
        self.start_day = 1
        self.start_date = datetime.date(self.start_year , self.start_month , self.start_day)
        self.url = 'http://www.thedailystar.net/newspaper?' + self.start_date.__str__()

        # Creating the Tagger object
        self.tagger = Tagger(classifier_path=STANFORD_CLASSIFIER_PATH, ner_path=STANFORD_NER_PATH)

        self.id = 0

        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        self.main_url = 'http://www.thedailystar.net'
        self.baseurl = 'http://www.thedailystar.net/newspaper?date='


        self.main_selection = response.xpath("//h5")

        for sel in self.main_selection:
            news_item = DailyStarItem()
            news_item['newspaper_section'] = sel.xpath("../../../../../../../div[1]/h2/text()").extract_first()
            news_item['url'] = self.main_url + sel.xpath("a/@href").extract_first()
            news_item['title'] = sel.xpath("a/text()").extract_first().strip()

            request = scrapy.Request(news_item['url'], callback=self.parseNews)

            request.meta['news_item'] = news_item
            yield request

        self.start_date = self.increase_day_by_one(self.start_date)

        self.next_page = self.baseurl + self.start_date.__str__()

        try:
            self.logger.info("TRYING")
            yield scrapy.Request(self.next_page, callback=self.parse)
        except:
            self.logger.info("PROBLEM")
            self.start_date = self.increase_day_by_one(self.start_date)
            self.next_page = self.baseurl + self.start_date.__str__()
            yield scrapy.Request(self.next_page, callback=self.parse)

    def parseNews(self, response):

        self.id += 1
        
        news_item = response.meta['news_item']
        
        #Getting the Article
        paragraphs = response.xpath("//div[@class='field-body view-mode-teaser']//p/text()").extract()
        news_item['article'] = ''.join([para.strip() for para in paragraphs])

        # Getting bottom tag line
        news_item['bottom_tag_line'] = response.xpath("//h2[@class='h5 margin-bottom-zero']/em/text()").extract_first()
        # Getting top tag line
        news_item['top_tag_line'] = response.xpath("//h4[@class='uppercase']/text()").extract_first()
        
        # Getting the published time
        news_item = self.getPublishedTime(news_item, response)

        # Getting the image source and captions
        news_item['images'] = response.xpath("//div[@class='caption']/../img/@src").extract()
        news_item['image_captions'] = response.xpath("//div[@class='caption']/text()").extract()

        # Get the breadcrumb
        news_item['breadcrumb'] = response.xpath("//div[@class='breadcrumb']//span[@itemprop='name']/text()").extract()

        # Get reporter
        news_item['reporter'] = response.xpath("//div[@class='author-name margin-bottom-big']/span/a/text()").extract_first()

        # Get the summary and keywords using 'newspaper' package
        # [WARNING : This section slows down the overall scraping process]
        article = Article(url=news_item['url'])
        article.download()
        article.parse()
        article.nlp()
        
        news_item['generated_summary'] = article.summary
        news_item['generated_keywords'] = article.keywords


        # Tagging the article
        try:
            self.tagger.entity_group(news_item['article'])
        except:
            print "NER Tagger exception"
        # Getting the ner tags
        news_item['ner_person'] = self.tagger.PERSON
        news_item['ner_organization'] = self.tagger.ORGANIZATION
        news_item['ner_time'] = self.tagger.TIME
        news_item['ner_percent'] = self.tagger.PERCENT
        news_item['ner_money'] = self.tagger.MONEY
        news_item['ner_location'] = self.tagger.LOCATION

        # ML tags
        news_item['ml_tags'] = None

        news_item['sentiment'] = self.tagger.get_indico_sentiment(news_item['article'])

        doc = {
            "news_url" : news_item['url'],
            "reporter" : news_item['reporter'],
            "published" : news_item['published_date'],
            "title" : news_item['title'],
            "content" : news_item['article'],
            "top_tagline" : news_item['top_tag_line'],
            "bottom_tagline" : news_item['bottom_tag_line'],
            "images" : news_item['images'],
            "image_captions" : news_item['image_captions'],
            "breadcrumb" : news_item['breadcrumb'],
            "sentiment" : news_item['sentiment'],
            "ml_tags" : None,
            "section" : news_item['newspaper_section'],
            "ner_person" : news_item['ner_person'],
            "ner_organization" : news_item['ner_organization'],
            "ner_money" : news_item['ner_money'],
            "ner_time" : news_item['ner_time'],
            "ner_location" : news_item['ner_location'],
            "ner_percent" : news_item['ner_percent'],
            "generated_keywords" : news_item['generated_keywords'],
            "generated_summary" : news_item['generated_summary'],
            "timestamp" : datetime.datetime.now(),
        }

        res = es.index(index="newspaper_index", doc_type='news', id=self.id, body=doc)

        # Data can be collected as csv also 
        yield doc

    def getPublishedTime(self, news_item, response):
        dt = response.xpath("//meta[@itemprop='datePublished']/@content").extract_first()
        converted_dt = datetime.datetime.strptime( dt.split("+")[0], "%Y-%m-%dT%H:%M:%S")
        formatted_dt = converted_dt.strftime("%Y-%m-%d %I:%M %p")
        news_item['published_date'] = formatted_dt
        return news_item
        
