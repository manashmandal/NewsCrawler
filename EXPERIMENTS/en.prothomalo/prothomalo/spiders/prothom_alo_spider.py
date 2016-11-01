import scrapy
import logging
import datetime

from prothomalo.items import News

class ProthomAloSpider(scrapy.Spider):
    name = 'prothomalo'

    def __init__(self, category):
        self.category = category

    def start_requests(self):
        self.url = 'http://en.prothom-alo.com/' + self.category +   '/news?page=1'
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        self.baseurl = 'http://en.prothom-alo.com/' + self.category + '/'

        self.main_selection = response.xpath("//div[@class='content_right']/h2[@class='title']/a")

        for sel in self.main_selection:
            
            news_item = News()

            news_item['url'] = self.baseurl + sel.xpath("@href").extract()[0]
            news_item['title'] = sel.xpath("text()").extract()[0]
            news_item['category'] = self.category

            request = scrapy.Request(news_item['url'], callback=self.parseNews)

            request.meta['news_item'] = news_item

            yield request

        next_page_path = response.xpath("//div[@class='pagination']/a[@class='next_page']/@href").extract()[0]

        next_page = self.baseurl + next_page_path

        if next_page_path is not None:
            yield scrapy.Request(next_page, callback=self.parse)


    def parseNews(self, response):
        self.logger.info("SCRAPING : " + response.url)
        
        news_item = response.meta['news_item']

        # Getting the content
        news_item = self.getContent(news_item, response)

        # Getting the reporter
        news_item = self.getReporter(news_item, response)

        # Getting the published time 
        news_item = self.getPublishedTime(news_item, response)

        # Getting the number of likes
        news_item = self.getLikeCount(news_item, response)

        yield {
            'TITLE' : news_item['title'],
            'PUBLISHED' : news_item['published'],
            'CONTENT' : news_item['content'],
            'REPORTER' : news_item['reporter'],
            'LIKE_COUNT' : news_item['likes'],
            'CRAWL_DATE' : datetime.date.today(),
            'NEWS_URL' : news_item['url']
        }

    def getContent(self, news_item ,response):
        news_content = ''.join(text for text in response.xpath("//div[@itemprop='articleBody']//p/text()").extract())
        news_item['content'] = news_content
        return news_item

    def getReporter(self, news_item, response):
        author = response.xpath("//span[@class='author']/text()").extract_first()
        news_item['reporter'] = author
        return news_item

    def getPublishedTime(self, news_item, response):
        time = response.xpath("//span[@itemprop='datePublished']/text()").extract()[0]
        news_item['published'] = time
        return news_item

    def getLikeCount(self, news_item, response):
        likecount = response.xpath("//span[@class='count mr5']/text()").extract_first()
        news_item['likes'] = likecount
        return news_item
