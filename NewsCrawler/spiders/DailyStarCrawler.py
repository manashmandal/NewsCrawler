import scrapy
import logging
import datetime
import re
from dateutil import parser

from NewsCrawler.items import DailyStarItem
from newspaper import Article

from NewsCrawler.Helpers.CustomNERTagger import Tagger
from NewsCrawler.Helpers.date_helper import increase_day_by_one, DATETIME_FORMAT, dateobject_to_split_date, date_to_string
from NewsCrawler.credentials_and_configs.stanford_ner_path import STANFORD_CLASSIFIER_PATH, STANFORD_NER_PATH
from NewsCrawler.Helpers.image_downloader import download_multiple_image

from scrapy.exceptions import CloseSpider

# Using elasticsearch and mongo
from elasticsearch import Elasticsearch
from pymongo import MongoClient

es = Elasticsearch()


class DailyStarSpider(scrapy.Spider):
    name="dailystar"

    def __init__(self, start_date, end_date, delimiter='-'):
        self.start_day, self.start_month, self.start_year = dateobject_to_split_date(
            start_date, delimiter=delimiter)  # [int(i) for i in start_date.split(delimiter)]
        self.end_day, self.end_month, self.end_year = dateobject_to_split_date(
            end_date, delimiter=delimiter)  # [int(i) for i in end_date.split(delimiter)]

    def start_requests(self):
        # Saving a copy of start date as begin date
        self.begin_date = datetime.date(
            self.start_year, self.start_month, self.start_day)

        # Will be updated as next date
        self.start_date = datetime.date(
            self.start_year, self.start_month, self.start_day)
        self.end_date = datetime.date(
            self.end_year, self.end_month, self.end_day)

        self.url = 'http://www.thedailystar.net/newspaper?' + 'date=' + self.start_date.__str__()

        # Creating the Tagger object
        self.tagger = Tagger(
            classifier_path=STANFORD_CLASSIFIER_PATH, ner_path=STANFORD_NER_PATH)

        self.id = 0

        # Creating mongo client
        client = MongoClient()
        self.db = client.news_db

        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        self.main_url = 'http://www.thedailystar.net'
        self.baseurl = 'http://www.thedailystar.net/newspaper?date='

        self.main_selection = response.xpath("//h5")

        for sel in self.main_selection:
            news_item = DailyStarItem()
            news_item['newspaper_name'] = 'The Daily Star'
            news_item['newspaper_section'] = sel.xpath(
                "../../../../../../../div[1]/h2/text()").extract_first()
            news_item['url'] = self.main_url + \
                sel.xpath("a/@href").extract_first()
            #news_item['title'] = sel.xpath("a/text()").extract_first().strip()

            request = scrapy.Request(news_item['url'], callback=self.parseNews)

            request.meta['news_item'] = news_item
            yield request

        self.start_date = increase_day_by_one(self.start_date)

        self.next_page = self.baseurl + self.start_date.__str__()

        # Crawling termination condition
        if self.start_date > self.end_date:
            raise CloseSpider(
                'Done scraping from ' + self.begin_date.__str__() + ' upto ' + self.end_date.__str__())

        try:
            self.logger.info("TRYING")
            yield scrapy.Request(self.next_page, callback=self.parse)
        except:
            self.logger.info("PROBLEM")
            self.start_date = increase_day_by_one(self.start_date)
            self.next_page = self.baseurl + self.start_date.__str__()
            yield scrapy.Request(self.next_page, callback=self.parse)

    # Returns snake_case string 
    def format_string(self, s):
        try:
            s = str(s.lower()).encode('ascii', 'ignore')
        except:
            s = ''
        # Remove all non-word characters (everything except numbers and letters)
        s = re.sub(r"[^\w\s]", '', s)

        # Replace all runs of whitespace with a single dash
        s = re.sub(r"\s+", '_', s)

        return s

    # Formula for id = newspaper_name + published_date + crawled_date
    def get_id(self, news_item, response):
        news_item = response.meta['news_item']
        # newspaper name
        nn = str(news_item['newspaper_name']).lower().replace(' ', '_')
        # Date published
        dp = date_to_string(news_item['published_date'], dateobject=False)
        # Date crawled
        dc = date_to_string(news_item['crawl_time'], dateobject=True)

        published_day, published_month, published_year = dp.split('_')
        crawled_day, crawled_month, crawled_year = dc.split('_')

        dp = published_year + '_' + published_month + '_' + published_day

        dc = crawled_year + '_' + crawled_month + '_' + crawled_day

        # id = nn + '_' + dp + '_' + dc

        # Converting news title into snakecase
        news_title = self.format_string(news_item['title'])[:15]

        id = nn + '_' + dp + '_' + news_title

        self.logger.info("ID: " + id)

        news_item['_id'] = id
        return news_item

    def parseNews(self, response):

        self.id += 1

        news_item = response.meta['news_item']

        

        # Getting the Article
        paragraphs = response.xpath(
            "//div[@class='field-body view-mode-teaser']//p/text()").extract()
        news_item['article'] = ''.join([para.strip() for para in paragraphs])

        # Add a space after punctuation [This is required, otherwise tagging
        # will combine two Named Entity into one]
        re.sub(r'\.(?! )', '. ', re.sub(r' +', ' ', news_item['article']))

        # Getting bottom tag line
        news_item['bottom_tag_line'] = response.xpath(
            "//h2[@class='h5 margin-bottom-zero']/em/text()").extract_first()
        # Getting top tag line
        news_item['top_tag_line'] = response.xpath(
            "//h4[@class='uppercase']/text()").extract_first()

        # Getting the published time
        news_item = self.getPublishedTime(news_item, response)

        # Getting the image source and captions
        news_item['images'] = response.xpath(
            "//div[@class='caption']/../img/@src").extract()
        news_item['image_captions'] = response.xpath(
            "//div[@class='caption']/text()").extract()

        # Get the breadcrumb
        news_item['breadcrumb'] = response.xpath(
            "//div[@class='breadcrumb']//span[@itemprop='name']/text()").extract()

        # Get reporter
        news_item['reporter'] = response.xpath(
            "//div[@class='author-name margin-bottom-big']/span/a/text()").extract_first()

        # Getting the title 
        news_item = self.getTitle(news_item, response)

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

        # Contains all occurances
        news_item['ner_list_person'] = self.tagger.LIST_PERSON
        news_item['ner_list_organization'] = self.tagger.LIST_ORGANIZATION
        news_item['ner_list_time'] = self.tagger.LIST_TIME
        news_item['ner_list_money'] = self.tagger.LIST_MONEY
        news_item['ner_list_location'] = self.tagger.LIST_LOCATION
        news_item['ner_list_percent'] = self.tagger.LIST_PERCENT

        # ML tags
        news_item['ml_tags'] = None

        try:
            news_item['sentiment'] = self.tagger.get_indico_sentiment(news_item[
                                                                      'article'])
        except:
            news_item['sentiment'] = None

        news_item['crawl_time'] = datetime.datetime.now(
        ).strftime(DATETIME_FORMAT)


        news_item = self.get_id(news_item, response)
        # news_item['_id'] = self.id

        # If there's image download it
        if (len(news_item['images']) > 0):
            download_multiple_image(news_item)

        doc = {
            "id": news_item['_id'],
            "news_url": news_item['url'],
            "newspaper": news_item['newspaper_name'],
            "reporter": news_item['reporter'],
            "about_reporter": None,
            "date_published": parser.parse(news_item['published_date']),
            "title": news_item['title'],
            "content": news_item['article'],
            "top_tagline": news_item['top_tag_line'],
            "bottom_tagline": news_item['bottom_tag_line'],
            "images": news_item['images'],
            "image_captions": news_item['image_captions'],
            "breadcrumb": news_item['breadcrumb'],
            "sentiment": news_item['sentiment'],

            "ml_tags": None,
            "category": None,
            "shoulder": None,
            "section": news_item['newspaper_section'],

            "ner_unique_person": news_item['ner_person'],
            "ner_unique_organization": news_item['ner_organization'],
            "ner_unique_money": news_item['ner_money'],
            "ner_unique_time": news_item['ner_time'],
            "ner_unique_location": news_item['ner_location'],
            "ner_unique_percent": news_item['ner_percent'],

            "ner_person": news_item['ner_list_person'],
            "ner_organization": news_item['ner_list_organization'],
            "ner_money": news_item['ner_list_money'],
            "ner_time": news_item['ner_list_time'],
            "ner_location": news_item['ner_list_location'],
            "ner_percent": news_item['ner_list_percent'],

            "generated_keywords": news_item['generated_keywords'],
            "generated_summary": news_item['generated_summary'],
            "date_crawled": datetime.datetime.now()
        }

        # inserting data into Elasticsearch [UNCOMMENT WHEN USING
        # ELASTICSEARCH]
        res = es.index(index="newspaper_index", doc_type='news', body=doc)
        # Inserting data into mongodb
        self.db.news_db.insert_one(doc)
        # Data can be collected as csv/json also
        yield doc

    def getPublishedTime(self, news_item, response):
        dt = response.xpath(
            "//meta[@itemprop='datePublished']/@content").extract_first()
        converted_dt = datetime.datetime.strptime(
            dt.split("+")[0], "%Y-%m-%dT%H:%M:%S")
        formatted_dt = converted_dt.strftime(DATETIME_FORMAT)
        news_item['published_date'] = formatted_dt
        return news_item

    def getTitle(self, news_item, response):
        try:
            title = response.xpath("//h1/text()").extract_first().strip()
        except:
            title = response.xpath("//h1/text()").extract_first()
        news_item['title'] = title
        return news_item
