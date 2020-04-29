# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class UserItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    name = scrapy.Field()
    avatar_url = scrapy.Field()
    headline = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    urlToken = scrapy.Field()
    gender = scrapy.Field()
    cover_url = scrapy.Field()
    type = scrapy.Field()
    badge = scrapy.Field()
    followerCount = scrapy.Field()
    followingCount = scrapy.Field()
