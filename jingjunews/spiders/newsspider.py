#coding:utf-8
import scrapy
# from selenium import common
# import selenium
# from selenium import webdriver
from jingjunews.items import JingjunewsItem
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import urllib
import time


DATE_FORMAT = '%Y-%m-%d'

def getTimeStr(timestr):
    #  %Y-%m-%d / %Y-%m-%d %H:%M:%S
    if timestr.find(u':') >= 0:
        timearray = time.strptime(timestr, '%Y-%m-%d %H:%M:%S')
    else:
        timearray = time.strptime(timestr, '%Y-%m-%d')
    newstime = time.strftime(DATE_FORMAT,timearray)
    return newstime

class JingjunewsSpider(scrapy.Spider):
    """docstring for JingjunewsSpider"""

    name = "jingjunews"

    #allowed_domains = []

    start_urls = ["http://cnpoc.cn/channels/19.html",
                   "http://cnpoc.cn/channels/20.html",
                    "http://cnpoc.cn/channels/21.html",
                    "http://www.jingju.com/jingjuxinwen/jingjuhuati/",
                    "http://www.jingju.com/jingjuxinwen/jingjuzhuanti/",
                    "http://www.jingju.com/jingjuxinwen/jingjushikan/",
                    "http://www.jingju.com/jingjuxinwen/yanchudongtai/",
                    "http://www.jingju.com/jingjuxinwen/renwuxinwen/",
                    "http://www.jingju.com/jingjuxinwen/jingdianwen/",
                    # "http://www.jingju.com/video/shipinxinwen/",  #视频新闻
                    "http://www.jingju.com/jingjuxinwen/wenhuadongtai/",
                    "http://www.jingju.com/jingjuxinwen/huodongzhaoji/",
                    "http://www.jingju.com/jingjuxinwen/piaoshedongtai/",
                    "http://www.tjjjy.com/cn/ynxw/index_1.html",
                    "http://www.tjjjy.com/cn/lyxw/index_1.html",
                    "http://history.xikao.com/history"
                    ]

    def parse(self, response):
        url = response.url
        self.mdate = getTimeStr(self.mdate)     #上次更新最后记录时间
        self.mdatesec = time.mktime(time.strptime(self.mdate, DATE_FORMAT))
        dispatcher.connect(self.onQuit, signals.spider_closed)
        
        if url.find('cnpoc.cn') >= 0:            # 国家京剧院
            yield scrapy.Request(url, callback=self.parse_cnpoc)

        elif url.find('nacta.edu.cn') >= 0:      # 中国戏曲学院
            yield scrapy.Request(url, callback=self.parse_nacta)

        elif url.find('tjjjy.com') >= 0:         # 天津京剧院
            yield scrapy.Request(url, callback=self.parse_tjjjy)

        elif url.find('jingju.com') >= 0:         # 京剧艺术网
            yield scrapy.Request(url, callback=self.parse_jingju)

        elif url.find('xikao.com') >= 0:         # 戏考网
            yield scrapy.Request(url, callback=self.parse_xikao)


    def parse_cnpoc(self, response):

        lines = response.xpath('//ul[@class="txt_list_info"]/li')
        titles = lines.xpath('a/text()').extract()
        titles.reverse()    
        urls = lines.xpath('a/@href').extract()
        urls.reverse()   
        dates = lines.xpath('span/text()').extract()
        dates.reverse()  # 按时间从远到近排序，pop出最近条目

        while len(dates) > 0:
            date = dates.pop()
            if self.processed(date):    # date不晚于上次update
                return
            else:
                new_url = 'http://cnpoc.cn' + urls.pop()
                yield scrapy.Request(new_url, callback=self.parse_item_cnpoc)

        navis = response.xpath('//div[@class="ipage"]')
        hrefs = navis.xpath('a/text()').extract()
        texts = navis.xpath('a/text()').extract()
        for i in xrange(0,len(texts)):
            if texts[i] == u'下一页':
                new_url = 'http://cnpoc.cn' + hrefs[i]
                yield scrapy.Request(new_url, callback=self.parse_cnpoc)
                break


    def parse_item_cnpoc(self, response):

        textbox = response.xpath('//div[@class="pic_list_box"]')

        title = textbox.xpath('h2/text()').extract()[0]
        timestr = textbox.xpath('p/span/text()').extract()[1].split(u'发布日期：')[-1]
        newstime = getTimeStr(timestr)
        text = response.xpath('//div[@class="zl_box"]')[0].extract()

        item = JingjunewsItem()
        item['title'] = title
        item['time'] = newstime
        item['source'] = u'国家京剧院'
        item['text'] = text
        item['url'] = response.url
        yield item

    def parse_tjjjy(self, response):
        print "tjjjy"
        lines = response.xpath('//div[@id="ny_left_content_dsj_list"]')
        titles = lines.xpath('table/tr/td/a/text()').extract()
        titles.reverse()
        urls = lines.xpath('table/tr/td/a/@href').extract()
        urls.reverse()
        dates = lines.xpath('table/tr/td/text()').extract()
        dates.reverse()

        while len(dates) > 0:
            date = dates.pop()
            if self.processed(date):   # 不晚于last update
                return
            else:
                new_url = "http://www.tjjjy.com" + urls.pop()
                print new_url
                yield scrapy.Request(new_url, callback = self.parse_item_tjjjy)

        navis = response.xpath('//div[@id="ny_list_fanye"]/table/tr/td')
        hrefs = navis.xpath('a/@href').extract()
        texts = navis.xpath('a/text()').extract()

        for i in xrange(0,len(hrefs)):
            if texts[i] == u'下页':
                new_url = "http://www.tjjjy.com" + hrefs[i]
                yield scrapy.Request(new_url, callback = self.parse_tjjjy)


    def parse_item_tjjjy(self, response):
        # http://www.tjjjy.com/cn/ynxw/20161101/09305893.html
        print response.url
        title = response.xpath('//p[@id="ny_dsjcon_tittle"]/text()')[0].extract()
        timestr = response.xpath('//p[@id="ny_time1"]/text()')[0].extract()
        newstime = getTimeStr(timestr)
        content = response.xpath('//div[@id="ny_dsjcon_content"]')[0].extract()

        item = JingjunewsItem()
        item['title'] = title
        item['time'] = newstime
        item['source'] = u'天津京剧院'
        item['text'] = content
        item['url'] = response.url
        yield item

    def parse_jingju(self, response):
        # http://www.jingju.com/jingjuxinwen/jingjushikan/

        lines = response.xpath('//div[@class="box"]/ul/li')
        titles = lines.xpath('span/a/text()').extract()
        titles.reverse()
        urls = lines.xpath('span/a/@href').extract()
        urls.reverse()
        dates = lines.xpath('span/text()').extract()
        dates.reverse()
        for i in xrange(1,len(dates)):
            if u'·' in dates:
                dates.remove(u'·')
                i = i - 1

        while len(dates) > 0:
            date = dates.pop()      # format as [2017-03-17]
            date = date.split('[')[-1].split(']')[0]
            if self.processed(date):   # date不晚于last update
                return
            else:
                new_url = "http://www.jingju.com" + urls.pop()
                print new_url
                yield scrapy.Request(new_url, callback = self.parse_item_jingju)

        href = response.xpath('//a[@class="pagination_next"]/@href').extract()
        for x in href:
            new_url = "http://www.jingju.com" + x
            yield scrapy.Request(new_url, callback = self.parse_jingju)

    def parse_item_jingju(self, response):
        title = response.xpath('//h1[@class="title"]/text()')[0].extract()
        htnote = response.xpath('//p[@class="htnote"]/span/text()')
        newstime = ''
        source = ''
        for span in htnote:
            if span.extract().find(u'时间：') >= 0:
                timestr = span.extract().split(u'时间：')[-1]
                newstime = getTimeStr(timestr)
            elif span.extract().find(u'来源：') >= 0:
                source = span.extract().split(u'来源：')[-1]
                if source == u'':
                    source = u'京剧艺术网'

        content = response.xpath('//div[@class="content"]')[0].extract()


        item = JingjunewsItem()
        item['title'] = title
        item['time'] = newstime
        item['source'] = source
        item['text'] = content
        item['url'] = response.url
        yield item


    def parse_nacta(self, response):
        #  中国戏曲学院，多为院方新闻，其中“媒体国戏”为与国戏相关的媒体新闻
        pass

    def parse_item_nacta(self, response):
        pass

    def parse_xikao(self, response):
        # http://history.xikao.com/history
        # http://history.xikao.com/history/2017/4

        pass

    def parse_item_xikao(self, response):
        pass

    def processed(self, date):
        # return weather date is earlier or same as than self.date
        # if date is late than self.date, return False
        if time.mktime(time.strptime(date, DATE_FORMAT)) - self.mdatesec > 0:
            return False
        return True

    def onQuit(self):
      print 'spider Closed!'
