import scrapy
import logging
import datetime

from NewsCrawler.items import ProthomAloItem
from newspaper import Article

from NewsCrawler.Helpers.CustomNERTagger import Tagger
from NewsCrawler.credentials_and_configs.stanford_ner_path import STANFORD_CLASSIFIER_PATH, STANFORD_NER_PATH

from NewsCrawler.Helpers.date_helper import dateobject_to_split_date

from scrapy.exceptions import CloseSpider

from elasticsearch import Elasticsearch

es = Elasticsearch()

class ProthomAloSpider(scrapy.Spider):
    name = 'prothomalo'

    def __init__(self, start_date="01-07-2014", end_date="02-07-2014", delimiter='-'):
        self.start_day, self.start_month, self.start_year = dateobject_to_split_date(start_date)
        self.end_day, self.start_month, self.end_year = dateobject_to_split_date(end_date)
    
    def start_requests(self):
        self.begin_date = datetime.date(self.start_year, self.start_month, self.start_day)

        self.start_date = datetime.date(self.start_year, self.start_month, self.start_day)
        self.end_date = datetime.date(self.start_year, self.start_month, self.start_day)

        self.main_url = 'http://en.prothom-alo.com'
        self.url = 'http://en.prothom-alo.com/archive/' + self.start_date.__str__()
    
        # Creating the tagger object
        self.tagger = Tagger(classifier_path=STANFORD_CLASSIFIER_PATH, ner_path=STANFORD_NER_PATH)

        self.id = 0

        yield scrapy.Request(self.url, self.parse)
    
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
                news_item['reporter'] = sel.xpath("div/span[1]/text()").split('.')[0] 
                news_item['published_date'] = sel.xpath("div/span[2]/text()").extract_first().strip()

            news_item['last_update'] = news_item['published_date']
    
    def get_location(self, inp):
        inp_list = inp.split('.')
        if (len(inp_list) < 2):
            return None
        return inp_list[-1].strip()