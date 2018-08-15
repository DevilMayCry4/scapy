# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem
from pw.items import PwItem
from pw.db.DBHelper import DBHelper


db = DBHelper()

class PwImagePipeline(ImagesPipeline):



    def get_media_requests(self, item, info):
        yield Request(item['imageUrl'])

    def item_completed(self, results, item, info):

        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            item['image'] = ''
            if isinstance(item,PwItem):
                db.insert(item)
            else:
                db.insertStarItem(item)
        else:
           item['image'] = image_paths[0]
           # 插入数据库
           if isinstance(item, PwItem):
                db.insert(item)
           else:
                db.insertStarItem(item)
        return item


class PwPipeline(object):



    def process_item(self, item, spider):
        return item




