# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class DailyStarItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    category = Field()
    newspaper_section = Field()
    reporter = Field()
    last_updated = Field()
    published_date = Field()
    article = Field()
    share_count = Field()
    comment_count = Field()
    title = Field()
    url = Field()
    breadcrumb = Field()
    images = Field()
    top_tag_line = Field()
    bottom_tag_line = Field()
    image_captions = Field()
    newspaper_name = Field()

    ml_tags = Field()
    sentiment = Field()


    # NER tags [only unique values]
    ner_person = Field()
    ner_money = Field()
    ner_time = Field()
    ner_organization = Field()
    ner_location = Field()
    ner_percent = Field()

    # Ner tags [considering all ocurrances]
    ner_list_person = Field()
    ner_list_money = Field()
    ner_list_time = Field()
    ner_list_organization = Field()
    ner_list_percent = Field()
    ner_list_location = Field()

    # These items are generated using 'newspaper' python package
    generated_keywords = Field()
    generated_summary = Field()