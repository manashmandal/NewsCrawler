# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class News(Item):
    category = Field()
    title = Field()
    url = Field()
    published = Field()
    updated = Field()
    content = Field()
    reporter = Field()
    image_urls = Field()
    tags = Field()
    likes = Field()

class NewsItem(Item):
    NewsCategory = Field()
    NewsTitle = Field()
    NewsURL = Field()

    # When it was published
    PublishedDate = Field()

    # Content
    Content = Field()

    # Reporter
    Reporter = Field()

    # Image
    ImageURL = Field()


# class News(Item):
#     # News Title
#     Title = Field()

#     # When it was published
#     PublishedDate = Field()

#     # Content
#     Content = Field()

#     # Reporter
#     Reporter = Field()

#     # Image
#     ImageURL = Field()

#     # Tag
#     Tag = Field()
