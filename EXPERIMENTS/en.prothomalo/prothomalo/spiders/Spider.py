import scrapy
from prothomalo.items import News, NewsItem
import logging

class ProthomaloSpider(scrapy.Spider):
    name = 'prothomalospider'


    allowed_domains = ["http://en.prothom-alo.com/"]

    # start_urls = [
    #     "http://en.prothom-alo.com/bangladesh/news?page=1"
    # ]

    def start_requests(self):
        url = 'http://en.prothom-alo.com/bangladesh/news?page=1'
        yield scrapy.Request(url, self.parse)


    def parse(self, response):
        baseurl = 'http://en.prothom-alo.com/bangladesh/news'
        self.wanted_num = 5
        self.main_selection = response.xpath("//div[@class='content_right']/h2[@class='title']/a")

        for sel in self.main_selection:
            #self.logger.info("Crawling news")
            News_Item = NewsItem()
            News_Item['NewsCategory'] = 'Bangladesh'
            News_Item['NewsTitle'] = sel.xpath("text()").extract()[0]
            News_Item['NewsURL'] = baseurl + sel.xpath("@href").extract()[0]
            # self.logger.info('News url is ' + News_Item['NewsURL'])
            yield scrapy.Request(str(News_Item['NewsURL']), callback=self.parseNews)
            # request.meta['News_Item'] = News_Item
            # yield request

    def parseNews(self, response):
        self.logger.info("Calllback time")

    # def parseNews(self, response):
    #     self.logger.info("PARSING NEWS")
    #     self.logger.info(response.url)
    #     News_Item = response.meta['News_Item']
    #     News_Item = self.getContent(News_Item, response)
    #     return News_Item
    #
    # def getContent(self, News_Item, response):
    #     News_Item['Content'] = ''.join(text for text in response.xpath("//div[@itemprop='articleBody']//p/text()").extract())
    #     self.logger.info("News item " + News_Item['Content'])
    #     print News_Item['Content']
    #     return News_Item

class AluSpider(scrapy.Spider):
    name = 'alu'

    def start_requests(self):
        self.url = 'http://en.prothom-alo.com/bangladesh/news?page=1'
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        self.baseurl = 'http://en.prothom-alo.com/bangladesh/'
        self.main_selection = response.xpath("//div[@class='content_right']/h2[@class='title']/a")

        for sel in self.main_selection:

            #Adding extrac things
            News_Item = NewsItem()
            News_Item['NewsCategory'] = 'Bangladesh'
            News_Item['NewsTitle'] = sel.xpath("text()").extract()[0]
            News_Item['NewsURL'] = self.baseurl + sel.xpath("@href").extract()[0]

            self.logger.info("TITLE: " + News_Item['NewsTitle'])

            theurl = self.baseurl + sel.xpath("@href").extract()[0]
            self.logger.info("URL : " + theurl)
            request = scrapy.Request(News_Item['NewsURL'], callback=self.parseNews)
            request.meta['News_Item'] = News_Item
            yield request

    def parseNews(self, response):
        self.logger.info("CALLBACK TIME")
        #self.logger.info(self.getNewsContent(response))

    def getNewsContent(self, response):
        return ''.join(text for text in response.xpath("//div[@itemprop='articleBody']//p/text()").extract())


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        url = 'http://quotes.toscrape.com/'
        tag = getattr(self, 'tag', None)
        if tag is not None:
            url = url + 'tag/' + tag
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('span small a::text').extract_first(),
            }

        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, self.parse)
