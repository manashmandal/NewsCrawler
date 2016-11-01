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

class ExperimentalSpider(scrapy.Spider):
    name = 'alup'

    def start_requests(self):
        self.url = 'http://en.prothom-alo.com/bangladesh/news?page=1'
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        self.logger.info("NOW ON PAGE: " + response.url)
        self.baseurl = 'http://en.prothom-alo.com/bangladesh/'
        self.main_selection = response.xpath("//div[@class='content_right']/h2[@class='title']/a")

        for sel in self.main_selection:
            urltoscrape = self.baseurl + sel.xpath("@href").extract()[0]
            yield scrapy.Request(urltoscrape, callback=self.parseNews)

        next_page = self.baseurl + response.xpath("//div[@class='pagination']/a[@class='next_page']/@href").extract()[0]

        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse)


    def parseNews(self, response):
        self.logger.info("SCRAPING : " + response.url)






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

            #self.logger.info("TITLE: " + News_Item['NewsTitle'])

            theurl = self.baseurl + sel.xpath("@href").extract()[0]
            #self.logger.info("URL : " + theurl)
            request = scrapy.Request(News_Item['NewsURL'], callback=self.parseNews)
            request.meta['News_Item'] = News_Item
            yield request


    def parseNews(self, response):
        self.logger.info("CALLBACK TIME")
        News_Item = response.meta['News_Item']
        News_Item = self.getNewsContent(News_Item, response)
        News_Item = self.getNewsReporter(News_Item, response)
        #self.logger.info(self.getNewsContent(response))
        #self.logger.info("PRINTING NEWS: " + News_Item['Content'])

        yield {
            'Title ' : News_Item['NewsTitle'],
            'Content '  : News_Item['Content']
        }

    def getNewsContent(self, item ,response):
        content = ''.join(text for text in response.xpath("//div[@itemprop='articleBody']//p/text()").extract())
        item['Content'] = content
        #return ''.join(text for text in response.xpath("//div[@itemprop='articleBody']//p/text()").extract())
        return item

    def getNewsReporter(News_Item, response):
        pass


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
