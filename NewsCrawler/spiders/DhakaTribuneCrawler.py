import scrapy
import logging
import datetime

from NewsCrawler.items import DhakaTribuneItem
from newspaper import Article

from NewsCrawler.Helpers.CustomNERTagger import Tagger
from NewsCrawler.Helpers.date_helper import increase_day_by_one, DATETIME_FORMAT, dateobject_to_split_date
from NewsCrawler.credentials_and_configs.stanford_ner_path import STANFORD_CLASSIFIER_PATH, STANFORD_NER_PATH

from scrapy.exceptions import CloseSpider

from elasticsearch import Elasticsearch

es = Elasticsearch()

class DhakaTribuneSpider(scrapy.Spider):
	name = 'dhakatribune'

	def __init__(self, start_page=0, end_page=2):
		self.start_page = int(start_page)
		self.end_page = int(end_page)

	def start_requests(self):
		self.begin_page = str(self.start_page)

		#Begin scraping from here
		self.base_url = 'http://archive.dhakatribune.com/archive?page=' + str(self.start_page)

		self.id = 0

		yield scrapy.Request(self.base_url, self.parse)

	
	def parse(self, response):
		self.main_selection = response.xpath("//div[@class='post-inner']")

		for selection in self.main_selection:
			news_item = DhakaTribuneItem()
			news_item['newspaper_name'] = 'Dhaka Tribune'
			news_item['url'] = selection.xpath("header/h2/a/@href").extract_first()
			news_item['published_date'] = selection.xpath("header/div[1]/text()").extract_first()
			news_item['excerpt'] = selection.xpath("div[1]/p/text()").extract_first().strip()
			news_item['reporter'] = xpath("header/div[1]/span/a/text()").extract_first()
			# request = scrapy.Request(news_item['url'], callback=self.parseNews)
			# request.meta['news_item'] = news_item

			yield {
				'url' : news_item['url'],
				'published date' : news_item['published_date']
			}

		# increase page count by one
		self.start_page += 1

		# Next page url 
		self.next_page = self.base_url + str(self.start_page)

		if self.start_page > self.end_page:
			raise CloseSpider('Done scraping from page: ' + str(self.begin_page) + ' to ' + str(self.end_page))
		
		try:
			self.logger.info("TRYING")
			yield scrapy.Request(self.next_page, callback=self.parse)
		except:
			self.logger.info("PROBLEM")
			self.start_page += 1
			self.next_page = self.base_url + str(self.start_page)
			yield scrapy.Request(self.next_page, callback=self.parse)


