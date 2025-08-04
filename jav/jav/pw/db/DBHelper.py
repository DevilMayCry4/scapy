# -*- coding: utf-8 -*-

import pymysql
from twisted.enterprise import adbapi
from scrapy.utils.project import get_project_settings  #导入seetings配置


class DBHelper():
    '''这个类也是读取settings中的配置，自行修改代码进行操作'''

    def __init__(self,query):
        settings = get_project_settings()  #获取settings配置，设置需要的信息

        dbparams = dict(
            host=settings['MYSQL_HOST'],  #读取settings中的配置
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',  #编码要加上，否则可能出现中文乱码问题
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        #**表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        if(query==False):
            dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
            self.dbpool = dbpool
        else:
            connect = pymysql.connect(host = '127.0.0.1',user = 'root' ,passwd='' ,port= 3306 ,db='pw' ,charset='utf8' )
            self.cur = connect.cursor()


    def connect(self):
        return self.dbpool

    #创建数据库
    def insert(self, item):
        sql = "insert into av(name,imageUrl,genreName," \
              "genre,star,starName," \
              "number,studio,series,seriesName,image,time,date,chinese) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        #调用插入的方法
        query = self.dbpool.runInteraction(self._conditional_insert, sql, item)
        #调用异常处理方法
        query.addErrback(self._handle_error)

        return item

    #写入数据库中
    def _conditional_insert(self, tx, sql, item):
        params = (item["name"], item['imageUrl'], item['genreName'],
                  item['genre'], item['star'], item['starName'],
                  item['number'],item['studio'],item['series'],item['seriesName'],item['image'],item['time'],item['date'],item['chinese'])
        tx.execute(sql, params)


    def _handle_error(self, failue):
        print('--------------database operation exception!!-----------------')
        print(failue)


    def insertStarItem(self,item):
        sql = "insert into star(name,imageUrl," \
              "xiongwei,yaowei,height," \
              "tunwei,birth,code,cup) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        # 调用插入的方法
        query = self.dbpool.runInteraction(self.starConditionalInsert, sql, item)
        # 调用异常处理方法
        query.addErrback(self._handle_error)

        return item

    def starConditionalInsert(self, tx, sql, item):
        params = (item["name"], item['imageUrl'],
                  item['xiongwei'], item['yaowei'], item['height'],
                  item['tunwei'], item['birth'], item['code'],item['cup'])
        tx.execute(sql, params)

    def inserGenreItem(self,item):
        sql = "insert into genre(name,genre) values(%s,%s)"
        # 调用插入的方法
        query = self.dbpool.runInteraction(self.genreConditionalInsert, sql, item)
        # 调用异常处理方法
        query.addErrback(self._handle_error)

        return item

    def genreConditionalInsert(self, tx, sql, item):
        params = (item["name"], item['genre'])
        tx.execute(sql, params)

    def insertAVLink(self,item):
        sql = "insert into link(number,link,domain ) values(%s,%s,%s)"
        # 调用插入的方法
        query = self.dbpool.runInteraction(self.AVLinkConditionalInsert, sql, item)
        # 调用异常处理方法
        query.addErrback(self._handle_error)

    def AVLinkConditionalInsert(self,tx,sql,item):
        params = (item['number'],item['link'],item['domain'])
        tx.execute(sql, params)

    def getPoint(self,number):
        return  self.dbpool.runQuery("select point from link where number = '%s'" + number)

    def isExistLink(self,number):
        s = ("select   IF( exists ( select * from link where number = '%s'), 1, 0) as result")%number
        self.cur.execute(s)
        r = self.cur.fetchall()[0][0]
        return  r == 1

    def isExistAV(self,number):
        s = ("select   IF( exists ( select * from  av a inner join link b   where a.number = b.number and a.number =  '%s' and b.link != '' ), 1, 0) as result") % number
        self.cur.execute(s)
        r = self.cur.fetchall()[0][0]
        result = r == 1
        if result:
            print('exist ' + number )
        return result









