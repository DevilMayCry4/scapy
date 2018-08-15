# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PwItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    number = scrapy.Field()
    time = scrapy.Field()
    date = scrapy.Field()
    genre = scrapy.Field()
    image =  scrapy.Field()
    # 演員
    star = scrapy.Field()
    #製作商
    studio = scrapy.Field()
    # 發行商
    label = scrapy.Field()
    # 系列
    series = scrapy.Field()

    imageUrl = scrapy.Field()

    genreName = scrapy.Field()

    seriesName = scrapy.Field()

    starName = scrapy.Field()


class StarItem(scrapy.Item):
    name = scrapy.Field()
    image = scrapy.Field()
    imageUrl = scrapy.Field()
    xiongwei = scrapy.Field()
    yaowei = scrapy.Field()
    height = scrapy.Field()
    tunwei = scrapy.Field()
    birth = scrapy.Field()
    code = scrapy.Field()
    cup = scrapy.Field()

