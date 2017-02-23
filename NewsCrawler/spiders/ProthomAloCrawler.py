import scrapy
import logging
import datetime
import re
from dateutil import parser

from NewsCrawler.items import ProthomAloItem
from newspaper import Article
from NewsCrawler.Helpers.CustomNERTagger import Tagger
from NewsCrawler.Helpers.image_downloader import download_image
from NewsCrawler.credentials_and_configs.stanford_ner_path import STANFORD_CLASSIFIER_PATH, STANFORD_NER_PATH
from NewsCrawler.Helpers.date_helper import dateobject_to_split_date, DATETIME_FORMAT, increase_day_by_one, date_to_string, d2s
from scrapy.exceptions import CloseSpider
from elasticsearch import Elasticsearch
from pymongo import MongoClient


es = Elasticsearch()


class ProthomAloSpider(scrapy.Spider):
    name="prothomalo"

    def __init__(self, start_date="01-07-2014", end_date="02-07-2014", delimiter='-'):
        self.start_day, self.start_month, self.start_year = dateobject_to_split_date(start_date, delimiter=delimiter)
        self.end_day, self.end_month, self.end_year = dateobject_to_split_date(end_date, delimiter=delimiter)
    
    def start_requests(self):
        self.begin_date = datetime.date(self.start_year, self.start_month, self.start_day)

        self.start_date = datetime.date(self.start_year, self.start_month, self.start_day)
        self.end_date = datetime.date(self.end_year, self.end_month, self.end_day)

        self.main_url = 'http://en.prothom-alo.com'
        self.baseurl = 'http://en.prothom-alo.com/archive/'
        self.url = 'http://en.prothom-alo.com/archive/' + self.start_date.__str__()
    
        # Creating the tagger object
        self.tagger = Tagger(classifier_path=STANFORD_CLASSIFIER_PATH, ner_path=STANFORD_NER_PATH)

        self.id = 0
        client = MongoClient()
        self.db = client.news_db

        yield scrapy.Request(self.url, self.parse)

    # Formula for id = newspaper_name + published_date + crawled_date
    def get_id(self, news_item, response):
        news_item = response.meta['news_item']
        # newspaper name
        np = str(news_item['newspaper_name']).lower().replace(' ', '_')
        # Date published
        dp = d2s(parser.parse(news_item['published_date']))
        # Date crawled
        dc = d2s(news_item['crawl_time'], True)

        id = np + '_' + dp + '_' + dc

        news_item['_id'] = id
        return news_item
    
    def parse(self, response):
        # Selecting the list of news
        self.main_section = response.xpath("//div[@class='list list_square mb20']/ul/li")

        for sel in self.main_section:
            news_item = ProthomAloItem()
            news_item['newspaper_name'] = 'Prothom Alo'
            news_item['category'] = sel.xpath("h3/a/@href").extract_first().split('/')[0]
            news_item['url'] = self.main_url + sel.xpath("h3/a/@href").extract_first()
            news_item['title'] = sel.xpath("h3/a/text()").extract_first().strip()
            news_item['news_location'] = self.get_location(sel.xpath("div/span[1]/text()").extract_first())

            # Sometimes reporter - newslocation span is missing
            if (len(sel.xpath("div/span")) < 2):
                news_item['published_date'] = sel.xpath("div/span[1]/text()").extract_first().strip()
                news_item['reporter'] = None
            else:
                news_item['reporter'] = sel.xpath("div/span[1]/text()").extract_first().split('.')[0] 
                news_item['published_date'] = sel.xpath("div/span[2]/text()").extract_first().strip()

            news_item['last_update'] = news_item['published_date']

            request = scrapy.Request(news_item['url'], callback=self.parseNews)
            request.meta['news_item'] = news_item
            yield request

        self.start_date = increase_day_by_one(self.start_date)

        self.logger.info("INCREASED: " + self.start_date.__str__())

        self.next_page = self.baseurl + self.start_date.__str__()

        # Crawling termination condition
        if self.start_date > self.end_date:
            raise CloseSpider('Done scraping from '+ self.begin_date.__str__() + ' upto ' +  self.end_date.__str__())

        try:
            self.logger.info("TRYING")
            yield scrapy.Request(self.next_page, callback=self.parse)
        except:
            self.logger.info("PROBLEM OCCURED: INCREASING DAY BY ONE")
            self.start_date = increase_day_by_one(self.start_date)
            self.next_page = self.baseurl + self.start_date.__str__()
            yield scrapy.Request(self.next_page, callback=self.parse)


    def parseNews(self, response):
        self.logger.info("TRYING")
        self.id += 1

        # Retreiving news item
        news_item = response.meta['news_item']

        # Crawl time
        news_item['crawl_time'] = datetime.datetime.now()

        # Currently detects one image
        news_item['images'] = self.get_image_url(response.xpath("//img/@src").extract())

        # Currently gets one caption
        news_item['image_captions'] = response.xpath("//div[@itemprop='articleBody']//span/text()").extract_first()

        #Getting the article
        paragraphs = response.xpath("//div[@itemprop='articleBody']//p/text()").extract()
        news_item['article'] = "".join([para.strip() for para in paragraphs])

        # Add a space after punctuation [This is required, otherwise tagging will combine two Named Entity into one]
        re.sub(r'\.(?! )', '. ', re.sub(r' +', ' ', news_item['article']))

        # Getting the breadcrumb
        news_item['breadcrumb'] = response.xpath("//div[@class='breadcrumb']/ul/li/a/strong/text()").extract()

        # Applying NLP from newspaper package [WARNING: slows the overall process]
        article = Article(url=news_item['url'])
        article.download()
        article.parse()
        article.nlp()
        news_item['generated_summary'] = article.summary
        news_item['generated_keywords'] = article.keywords

        # Tagging the Article
        try:
            self.tagger.entity_group(news_item['article'])
        except:
            print "NER Tagger Exception"
            self.logger.info("NER Crashed")
        
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
        news_item['ner_list_percent'] = self.tagger.LIST_PERCENT
        news_item['ner_list_money'] = self.tagger.LIST_MONEY
        news_item['ner_list_location'] = self.tagger.LIST_LOCATION

        #ML Tags
        news_item['ml_tags'] = None

        news_item['sentiment'] = self.tagger.get_indico_sentiment(news_item['article'])

        news_item = self.get_id(news_item, response)

        # If image exists, download it
        if news_item['images'] != None:
            download_image(news_item)

        doc = {
            "id" : news_item['_id'],
            "news_url" : news_item['url'],
            "newspaper" : news_item['newspaper_name'],
            "reporter" : news_item['reporter'],
            "about_reporter" : None,
            "date_published" : parser.parse(news_item['published_date']),
            "title" : news_item['title'],
            "content" : news_item['article'],
            "top_tagline" : None,
            "bottom_tagline" : None,
            "images" : news_item['images'],
            "image_captions" : news_item['image_captions'],
            "breadcrumb" : news_item['breadcrumb'],
            "sentiment" : news_item['sentiment'],
            
            "ml_tags" : None,
            "category" : news_item['category'],
            "shoulder" : None,
            "section" : news_item['category'],
            
            "ner_unique_person" : news_item['ner_person'],
            "ner_unique_organization" : news_item['ner_organization'],
            "ner_unique_money" : news_item['ner_money'],
            "ner_unique_time" : news_item['ner_time'],
            "ner_unique_location" : news_item['ner_location'],
            "ner_unique_percent" : news_item['ner_percent'],

            "ner_person" : news_item['ner_list_person'],
            "ner_organization" : news_item['ner_list_organization'],
            "ner_money" : news_item['ner_list_money'],
            "ner_time" : news_item['ner_list_time'],
            "ner_location" : news_item['ner_list_location'],
            "ner_percent" : news_item['ner_list_percent'],

            "generated_keywords" : news_item['generated_keywords'],
            "generated_summary" : news_item['generated_summary'],
            "date_crawled" : datetime.datetime.now()
        }

        # Inserting data to Elasticsearch
        res = es.index(index="newspaper_index", doc_type="news", body=doc)
        # Inserting data into mongodb
        self.db.news_db.insert_one(doc)
        self.logger.info(res)
        # Output can also be saved as csv/json
        yield doc
    
    def get_location(self, inp):
        inp_list = inp.split('.')
        if (len(inp_list) < 2):
            return None
        return inp_list[-1].strip()

    def get_image_url(self, inp):
        for image_url in inp:
            if 'contents' and 'uploads' in image_url.split('/'):
                return self.main_url + image_url
