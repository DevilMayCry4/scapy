# -*- coding: utf-8 -*-

import scrapy
import os
import sys
import json
from urllib import parse
from  items import PwItem,StarItem,GenreItem,LinkItem

#existmag 有链接 mag ，所有all

AtressIndex = 0
magkey = 'all'
headers = {'user-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'}

class PWSpider(scrapy.Spider):
    name = "pw"
    def start_requests(self):
        #yield scrapy.Request(url='https://www.javbus.com/genre', headers=headers, callback=self.parseGenre)
        #yield scrapy.Request(url='https://www.javbus.com/SSNI-382',headers=headers,callback=self.parse)
        yield scrapy.Request(url='https://www.javbus.com/actresses', headers=headers, callback=self.parseAtress)

    def parseGenre(self,response):
        list = response.xpath(".//div[@class='row genre-box']")

        for l in list:
           x = l.xpath(".//a")
           for t in x:
               j = t.xpath(".//@href")[0]
               gener = j.extract().replace('https://www.javbus.com/genre/','')
               v = t.xpath(".//text()")[0].extract()
               item = GenreItem()
               item["name"] = v
               item["genre"] = gener
               yield item



    def parseAtress(self,response):
        global AtressIndex
        if AtressIndex >= 5600:
            return
        AtressIndex = AtressIndex + 1
        list = response.xpath('//*[@id="waterfall"]')[0].xpath('./div')
        for div in list:
            a = div.xpath(".//a/@href")
            if len(a) > 0:
                href = a[0].extract()
                yield scrapy.Request(url=href, headers=headers,cookies={'existmag':'mag'}, callback=self.parseStar)
        if len(response.xpath("//*[@id='next']")):
              link = response.xpath("//a[@id='next']")
              if len(link) > 0:
                 url = response.urljoin(link[0].xpath("./@href")[0].extract())
                 yield scrapy.Request(url=url, headers=headers,cookies={'existmag':'mag'}, callback=self.parseAtress)
        else:
            ul = response.xpath(".//ul[@class='pagination pagination-lg']")
            findActive = False
            if len(ul) > 0:
                lis = ul[0].xpath('.//li')
                for li in lis:
                    if li.extract().find('上一頁') != -1:
                        continue
                    elif len(li.xpath("@class")) > 0:
                        findActive = True
                        continue
                    elif findActive:
                        pageUlr = response.urljoin(li.xpath("./a/@href")[0].extract())
                        yield scrapy.Request(url=pageUlr, headers=headers, cookies={'existmag': 'mag'},
                                             callback=self.parseAtress)

    def parseStar(self,response):
        starDivs = response.xpath("//*[@class='avatar-box']")
        code = response.url.split('star/')[-1].split('/')[0]
        if len(starDivs)>0:
            starDiv = starDivs[0]
            imgItem = starDiv.xpath("./div[@class='photo-frame']/img")
            item = StarItem()
            item['code'] = code
            if len(imgItem) > 0:
                item["imageUrl"] = imgItem[0].xpath("./@src").extract()[0]
                item["name"] = imgItem[0].xpath("./@title").extract()[0]
            infos = response.xpath("//*[@class='photo-info']/p")
            keys = self.getConfig('starkeys.json')
            for key in keys:
                item[key] = ''
            for p in infos:
                for key in keys.keys():
                    value = keys[key]
                    pText = p.xpath("./text()").extract()[0]
                    if pText.find(value) != -1:
                        item[key] = pText.replace(value,'')


            yield  item

        waterfall = response.xpath('//*[@id="waterfall"]')[1]
        list = waterfall.xpath('./div')
        for div in list:
            a = div.xpath(".//a/@href")
            if len(a) > 0:
              href = a[0].extract()
              yield scrapy.Request(url=href, headers=headers, callback=self.parse)
        if len(response.xpath("//*[@id='next']")):
              link = response.xpath("//a[@id='next']")
              if len(link) > 0:
                 url = response.urljoin(link[0].xpath("./@href")[0].extract())
                 yield scrapy.Request(url=url, headers=headers,cookies={'existmag':'mag'}, callback=self.parseStar)
        else:
            ul = response.xpath(".//ul[@class='pagination pagination-lg']")
            findActive = False
            if len(ul) > 0:
                lis = ul[0].xpath('.//li')
                for li in lis:
                    if li.extract().find('上一頁') != -1:
                        continue
                    elif len(li.xpath("@class")) > 0:
                        findActive = True
                        continue
                    elif findActive:
                        pageUlr = response.urljoin(li.xpath("./a/@href")[0].extract())
                        yield scrapy.Request(url=pageUlr, headers=headers, cookies={'existmag': 'mag'},
                                             callback=self.parseStar)

    def parse(self, response):
        containers = response.xpath("//div[@class='container']")
        keys = self.getConfig('key.json')
        if len(containers) != 0:
            container = containers[0]
            item = PwItem()
            item['name'] = container.xpath(".//h3[1]/text()")[0].extract()
            imageUrl = container.xpath(".//div[contains(@class, 'screencap')][1]/a/@href").extract()[0]
            item['imageUrl'] = imageUrl
            info = container.xpath(".//div[contains(@class, 'info')][1]")
            ps = info.xpath(".//p")
            genrs = response.xpath(".//*[@class='genre']/a")
            genrKeys = ''
            names = ''
            for genr in genrs:
                genreHref = genr.xpath('@href')[0].extract()
                if genreHref.find('/genre/') != -1:
                    key = genreHref.rsplit('/', 1)[-1]
                    genrKeys += key +'|'
                    name =  genr.xpath('./text()')[0].extract()
                    names += name+'|'
            item['genreName'] = names
            item['genre'] = genrKeys
            item['image'] = ''
            item['series'] = ''
            item['seriesName'] = ''
            starList = ''
            startListName = ''
            spans = response.xpath("./body/div[5]/div[1]/div[2]/p[11]/span")
            if len(spans) >0:
                for span in spans:
                    starList  += span.xpath(".//a/@href")[0].extract().rsplit('/', 1)[-1] + '|'
                    startListName += span.xpath("./a/text()")[0].extract() + "|"

                item['star'] = starList
                item['starName'] = startListName
            else:
                starNames = response.xpath("//*[@class='star-box star-box-common star-box-up idol-box']")
                for starDiv in starNames:
                    starList += starDiv.xpath("./li/a")[0].xpath("@href")[0].extract().split('/')[-1] +'|'
                    startListName += starDiv.xpath("./li/div/a")[0].xpath("@title")[0].extract()+'|'


                item['star'] =starList
                item['starName']=startListName


            for p in ps:
                Pheaders =  p.xpath('.//span[1]/text()')
                if len(Pheaders) > 0:
                    header = Pheaders[0].extract()
                    for key in keys.keys():
                        if header.find(keys[key]) != -1:
                           a =  p.xpath('.//a[1]')
                           if len(a) > 0:
                               item[key] = a[0].xpath('@href')[0].extract().rsplit('/', 1)[-1]
                               if keys[key].find('系列') != -1:
                                   serise = a[0].xpath('./text()').extract()
                                   if len(serise) >0:
                                       item['seriesName'] = serise[0]

                           else:
                               span = p.xpath('.//span[2]/text()')
                               if len(span) > 0:
                                   item[key] = span[0].extract()
                               else:
                                   v = p.xpath("./text()")[0].extract()
                                   if len(v) != 0 and v != ':':
                                       item[key] = v
            number = item['number']
            linkUlr = 'https://u3c3.com/?search='+number
            yield scrapy.Request(url=linkUlr, headers=headers, cookies={'existmag': 'mag'}, callback=self.parseLink,meta={'number':number})
            yield item




    def findNextPage(self,response,block,headers):
        if len(response.xpath("//*[@id='next']")):
              link = response.xpath("//a[@id='next']")
              if len(link) > 0:
                 url = response.urljoin(link[0].xpath("./@href")[0].extract())
                 yield scrapy.Request(url=url, headers=headers,cookies={'existmag':'mag'}, callback=block)
        else:
            ul = response.xpath(".//ul[@class='pagination pagination-lg']")
            findActive = False
            if len(ul) > 0:
                lis = ul[0].xpath('.//li')
                for li in lis:
                    if li.extract().find('上一頁') != -1:
                        continue
                    elif len(li.xpath("@class")) > 0:
                        findActive = True
                        continue
                    elif findActive:
                        pageUlr = response.urljoin(li.xpath("./a/@href")[0].extract())
                        yield scrapy.Request(url=pageUlr, headers=headers, cookies={'existmag': 'mag'},
                                             callback=block)


    def stringToDict(self,cookie):
        itemDict = {}
        items = cookie.split(';')
        for item in items:
            key = item.split('=')[0].replace(' ', '')
            value = item.split('=')[1]
            itemDict[key] = value
        return itemDict

    def writeResponeToFile(self,str,path):
        with open(path,'w') as f:
            f.write(str)
            f.close()

    def getConfig(self, name):
        paths = sys.path
        dir = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(dir, 'config/' + name)
        item = None
        with open(path, 'r',encoding='utf-8') as f:
            item = json.loads(f.read())
        return item


#magnet 解析 https://u3c3.com/?search=
    def parseLink(self,response):
        item = LinkItem()
        item['link']=''
        number = response.meta['number']
        magents = response.xpath("//a/@href")
        item['number'] = number
        for magent in magents:
            href = magent.extract()
            if  href.find('magnet:?xt') != -1:
                item['link'] = href
                yield item
                return
        url = 'https://m.dongxingdi.com/list/'+number+'/1'
        yield scrapy.Request(url=url, headers=headers, cookies={'existmag': 'mag'}, callback=self.parseZhongziLink,
                                 meta={'number': number})





# magnet 解析  https://m.dongxingdi.com/list/xx/1
    def parseZhongziLink(self,response):
        item = LinkItem()
        item['link'] = ''
        number = response.meta['number']
        magents = response.xpath("//a/@href")
        item['number'] = number
        for magent in magents:
            href = magent.extract()
            key = '/info-'
            if href.find(key) != -1:
                item['link'] = 'magnet:?xt=urn:btih:' +  href.replace(key,'')
                yield item
                return
        yield item

