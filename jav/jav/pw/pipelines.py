# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem
from items import PwItem
import shutil
from db.DBHelper import DBHelper
from scrapy.pipelines.images import ImagesPipeline


from  items import PwItem,StarItem,GenreItem,LinkItem
from scrapy.utils.project import get_project_settings
import os


db = DBHelper(False)

class PwImagePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if isinstance(item,LinkItem):
            db.insertAVLink(item)
            return  None
        if isinstance(item,GenreItem):
            db.inserGenreItem(item)
            return  None
        if isinstance(item,StarItem):
            db.insertStarItem(item)
            return None

        yield Request(item['imageUrl'],meta={'parseStar':item['parseStar']})

    def item_completed(self, results, item, info):

        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            if isinstance(item,GenreItem):
                db.inserGenreItem(item)
            else:
                if isinstance(item,LinkItem):
                    db.insertAVLink(item)
                else:
                    if isinstance(item,PwItem):
                        item['image'] = ''
                        db.insert(item)
                    else:
                      db.insertStarItem(item)
        else:

           if isinstance(item, GenreItem):
                db.inserGenreItem(item)
           else:
                if isinstance(item,LinkItem):
                    db.insertAVLink(item)
                else:
                    if isinstance(item,PwItem):
                        item['image'] = image_paths[0]
                        db.insert(item)
                        # 插入数据库
                    else:
                      db.insertStarItem(item)
        imagePath = os.path.join(os.path.abspath(os.path.dirname(__file__)),get_project_settings().get('IMAGES_STORE'))
        if isinstance(item,PwItem) and (item['image'] != ''):
            if(item['parseStar']!= ''):
                dir = os.path.join(imagePath,'full')
                dir =  os.path.join(dir,item['parseStar'])
            if os.path.exists(dir) == False:
                os.mkdir(dir)
            src = os.path.join(imagePath,item['image'])
            shutil.move(src, os.path.join(dir,item['image'].split('/')[-1]))
        return item


class PwPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, GenreItem):
            db.inserGenreItem(item)




