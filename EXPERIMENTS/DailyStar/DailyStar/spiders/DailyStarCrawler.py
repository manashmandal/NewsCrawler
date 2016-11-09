import scrapy
import logging
import datetime

from DailyStar.items import DailyStarItem

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
        
        news_item = response.meta['news_item']

        news_item['bottom_tag_line'] = response.xpath("//h2[@class='h5 margin-bottom-zero']/em/text()").extract_first()
        news_item['top_tag_line'] = response.xpath("//h4[@class='uppercase']/text()").extract_first()
        news_item = self.getPublishedTime(news_item, response)


        yield {
            "News Title" : news_item['title'],
            "Published Date" : news_item['published_date']
        }

    def getPublishedTime(self, news_item, response):
        dt = response.xpath("//meta[@itemprop='datePublished']/@content").extract_first()
        converted_dt = datetime.datetime.strptime( dt.split("+")[0], "%Y-%m-%dT%H:%M:%S")
        formatted_dt = converted_dt.strftime("%Y-%m-%d %I:%M %p")
        news_item['published_date'] = formatted_dt
        return news_item
        