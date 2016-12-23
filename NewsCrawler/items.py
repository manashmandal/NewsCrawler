# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class DailyStarItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = Field()
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
    crawl_time = Field()

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


class ProthomAloItem(Item):
    _id = Field()
    category = Field()
    newspaper_name = Field()
    reporter = Field()
    news_location = Field()
    article = Field()
    title = Field()
    last_update = Field()
    published_date = Field()
    breadcrumb = Field()
    images = Field()
    ml_tags = Field()
    image_captions = Field()
    sentiment = Field()
    url = Field()
    crawl_time = Field()

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


class DhakaTribuneItem(Item):
    _id = Field()
    category = Field()
    newspaper_name = Field()
    reporter = Field()
    news_location = Field()
    article = Field()
    title = Field()
    last_update = Field()
    published_date = Field()
    breadcrumb = Field()
    images = Field()
    ml_tags = Field()
    image_captions = Field()
    sentiment = Field()
    url = Field()
    excerpt = Field()
    shoulder = Field()
    images_credit = Field()
    about_reporter = Field()
    crawl_time = Field()

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
