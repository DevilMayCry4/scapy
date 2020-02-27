# -*- coding: utf-8 -*-

import scrapy
import os
import sys
import json
from urllib import parse
from  items import PwItem,StarItem,GenreItem,LinkItem
from db.DBHelper import DBHelper

#existmag 有链接 mag ，所有all

PageCount = 0
magkey = 'all'
headers = {'user-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'}
ChineseHDPoint = 2
ChinesePoint = 1.5
HDPoint = 1.2
db = DBHelper(True)


class PWSpider(scrapy.Spider):
    name = "pw"
    def start_requests(self):
        keys = self.getConfig('star.json')
        for key in keys:
            url =  'https://www.javbus.com/star/' + key
            yield scrapy.Request(url=url, headers=headers, cookies={'existmag': 'mag'},
                                 callback=self.parseStar)

       # yield scrapy.Request(url='https://www.javbus.com/genre', headers=headers, callback=self.parseGenre)
       #yield scrapy.Request(url='https://www.javbus.com/JRZD-342',headers=headers,callback=self.parse,meta={'chinese':'1','parseStar':'mga'})
        #解析演员
        #yield scrapy.Request(url='https://www.javbus.com/actresses', headers=headers, callback=self.parseAtress)
        #解析列表
        #yield scrapy.Request(url='https://www.javbus.com', headers=headers, callback=self.parseContent)
       #yield  scrapy.Request(url='https://www.javbus.com/star/mga', headers=headers,cookies={'existmag':'mag'}, callback=self.parseStar,meta={'star':'mga'})
#yield scrapy.Request(url='https://torrentz2.eu/search?f=NDRA-067', headers=headers, callback=self.parseTorrent ,meta={'number': 'NDRA-067'})

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
        global PageCount
        if PageCount >= 500:
            return
        PageCount = PageCount + 1
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
        list = waterfall.xpath(".//*[@class='movie-box']")
        for div in list:
            photoInfo = div.xpath(".//*[@class='photo-info']")[0]
            href =  div.xpath(".//@href")[0].extract()
            chinese = '0'
            if photoInfo.extract().find('字幕') != -1:
                chinese = '1'
            if len(href) > 0:
              if (db.isExistAV(self.findNumber(href))):
                   continue
              yield scrapy.Request(url=href, headers=headers, callback=self.parse,meta={'chinese':chinese,'parseStar':code})


        if len(response.xpath("//*[@id='next']")):
              link = response.xpath("//a[@id='next']")
              if len(link) > 0:
                 url = response.urljoin(link[0].xpath("./@href")[0].extract())
                 yield scrapy.Request(url=url, headers=headers,cookies={'existmag':'mag'}, callback=self.parseStar,meta=response.meta)
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
                                             callback=self.parseStar,meta=response.meta)

    def parse(self, response):
        containers = response.xpath("//div[@class='container']")
        keys = self.getConfig('key.json')
        if len(containers) != 0:
            container = containers[0]
            item = PwItem()
            item['parseStar'] = response.meta['parseStar']
            item['chinese'] = response.meta['chinese']
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
            if db.isExistLink(number) == False:
                linkUlr = 'https://www.torrentkitty.tv/search/' + number
                yield scrapy.Request(url=linkUlr, headers=headers, cookies={'existmag': 'mag'},
                                     callback=self.parseTorrentKity,
                                     meta={'number': number})
                yield item
            else:
                print('exist-------- ' + number)
                yield item

    def findNumber(self,url):
       return  url.split('/')[-1]


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
            rd = f.read()
            item = json.loads(rd)
        return item


#解析最新内容
    def parseContent(self,response):
        global PageCount
        if PageCount >= 200:
            return
        PageCount += 1
        waterfall = response.xpath('//*[@id="waterfall"]')[1]
        list = waterfall.xpath(".//*[@class='movie-box']")
        for div in list:
            photoInfo = div.xpath(".//*[@class='photo-info']")
            href = div.xpath(".//@href")[0].extract()
            chinese = '0'
            l = photoInfo.extract()
            if (isinstance(l,str)) == False:
                l = photoInfo.extract()[0]
            if l.find('字幕') != -1:
                chinese = '1'
            if len(href) > 0:
                if (db.isExistAV(self.findNumber(href))):
                    continue
                yield scrapy.Request(url=href, headers=headers, callback=self.parse, meta={'chinese': chinese})

        if len(response.xpath("//*[@id='next']")):
            link = response.xpath("//a[@id='next']")
            if len(link) > 0:
                url = response.urljoin(link[0].xpath("./@href")[0].extract())
                yield scrapy.Request(url=url, headers=headers, cookies={'existmag': 'mag'}, callback=self.parseContent)
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
                                             callback=self.parseContent)

#中文1.5 HD-FHD 1.4
#magnet 解析 https://u3c3.com/?search=
    def parseLink(self,response):
        item = LinkItem()
        item['link']=''
        item['domain'] = 'u3c3'
        number = response.meta['number']
        tbody = response.xpath("//tbody")
        trs = tbody.xpath("//tr")
        point = 1
        link = ''
        for tr in trs:
            links = tr.xpath(".//td[3]//a[2]")
            if len(links) > 0:
                if tr.extract().find('中文') != -1 or tr.extract().find('HD') != -1:
                    tmpLink = tr.xpath(".//td[3]//a[2]")[0]
                    if(tr.extract().find('中文') != -1) and point < ChinesePoint:
                          point = ChinesePoint
                          link = tmpLink
                    if (tr.extract().find('HD') != -1) and point < HDPoint:
                        point = HDPoint
                        link = tmpLink
                    if tr.extract().find('中文') != -1 and tr.extract().find('HD') != -1:
                         point = ChineseHDPoint

                else:
                        link = tr.xpath(".//td[3]//a[2]")[0]
        if isinstance(link,str) == False:
            href = link.xpath('.//@href')[0]
            item['link'] = href.extract()
            item['number'] = number
            yield item
            return
        url = 'https://m.dongxingdi.com/list/'+number+'/1'
        yield scrapy.Request(url=url, headers=headers, cookies={'existmag': 'mag'}, callback=self.parseZhongziLink,
                               meta={'number': number})



# magnet 解析  https://m.dongxingdi.com/list/xx/1
    def parseZhongziLink(self, response):
        item = LinkItem()
        item['link'] = ''
        number = response.meta['number']
        magents = response.xpath("//a/@href")
        item['number'] = number
        item['domain'] = 'dongxingdi'
        for magent in magents:
            href = magent.extract()
            key = '/info-'
            if href.find(key) != -1:
                item['link'] = 'magnet:?xt=urn:btih:' + href.replace(key, '')
                yield item
                return






    def parseTorrent(self,response):
        number = response.meta['number']
        chinise = number + '-c'
        dls = response.xpath("//div[@class='results']//dl")
        for dl in dls:
            if dl.xpath(".//dt")[0].extract().lower().find(chinise.lower()) != -1 or dl.xpath(".//dt")[0].extract().find('中文') != -1   or dl.xpath(".//dt")[0].extract().lower().find('_c') != -1:
                tmp = dl.xpath(".//dt//a[@href]")[0].xpath(".//@href")[0].extract()
                link  = 'magnet:?xt=urn:btih:' + tmp.replace('/', '')
                item = LinkItem()
                item['link'] =  link
                item['number'] = number
                item['domain'] = 'torrent2'
                yield item
                return
        linkUlr = 'https://u3c3.com/?search=' + number
        yield scrapy.Request(url=linkUlr, headers=headers, cookies={'existmag': 'mag'}, callback=self.parseLink,meta={'number':number})


    def parseTorrentKity(self,response):
        number = response.meta["number"]
        if response.status != 403:
            tbody = response.xpath("//table[@id='archiveResult']//tbody")
            trs = response.xpath("//tr")
            for tr in trs:
                names = tr.xpath(".//td[@class='name']/text()")
                if len(names) == 1:
                    name = names[0].extract()
                    if name != 'Torrent Description' and self.isChineseString(name,number) and name.find('No result') == -1:
                        tmp = tr.xpath(".//td[@class='action']")[0].xpath(".//@href")[0].extract()
                        link = 'magnet:?xt=urn:btih:' + tmp.replace('/information/', '')
                        item = LinkItem()
                        item['link'] = link
                        item['number'] = number
                        item['domain'] = 'torrentkitty'
                        yield item
                        return


        linkUlr = 'https://torrentz2.eu/search?f=' + number
        yield scrapy.Request(url=linkUlr, headers=headers, cookies={'existmag': 'mag'},
                             callback=self.parseTorrent,
                             meta={'number': number})


    def isChineseString(self,str,number):
        key = number.replace('-','')
        searchString = str.replace('-','')
        searchString = searchString.replace(key,'').lower()
        return searchString.find('c') !=  -1 or searchString.find('中文') != -1 or searchString.find('字幕') != -1 or searchString.find('r') !=  -1




