import scrapy
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

from jukucrawl.items import Jukuplace

class YoyogimoshiSpider(scrapy.Spider):
    name = 'yoyogimoshi'
    allowed_domains = ['yozemi.ac.jp']
    start_urls = ['http://www.yozemi.ac.jp/moshi/schedule']
    re_fig = re.compile(".*maps.*")

    def parse(self, response):

        soup = BeautifulSoup(response.body, 'html.parser')

        for ls in soup.findAll("section", id=re.compile("anchor[0-9]*")):
            grade = ls.find("div", class_="section-title").h2.get_text()
            # print("MOSHI-NAME:{}".format(grade))
            
            for l in ls.findAll("p", class_="mod-link"):
                # print('url:{}'.format('http://www.yozemi.ac.jp' + l.a.attrs['href']))
                item = Jukuplace()
                item['grade'] = grade
                item['name'] = l.a.get_text().replace(' ','')
                req = scrapy\
                        .Request(response.urljoin('http://www.yozemi.ac.jp' + l.a.attrs['href']), \
                        self.parse_kaijo_list)
                req.meta['itm'] = item
                yield req

    def parse_kaijo_list(self, response):
        # print('URL:{}'.format(response.url))
        soup = BeautifulSoup(response.body, 'html.parser')

        date = soup.find("tbody", class_="mod-table_th-slim mod-table_td-slim th-align-center").tr.td.get_text()
        print("DATE:{}".format(date))
        response.meta['itm']['date'] = date

        #for hour in soup.findAll("tbody", class_="mod-table_th-xslim mod-table_td-xslim"):
        #    print("HOUR:{}".format(hour.tr.findAll("td")[1].get_text()))

        kaijou = soup.find("p", text="実施会場一覧はこちらへ").a
        # print('KAIJOU:{}'.format(kaijou.attrs['href']))
        req = scrapy.Request(response.urljoin(kaijou.attrs['href']), self.parse_kaijo)
        req.meta['itm'] = response.meta['itm']
        yield req

    def parse_kaijo(self, response):
        # print('URL:{}'.format(response.url))
        soup = BeautifulSoup(response.body, 'html.parser')
        
        tbls = soup.find("table", class_="mod-table")
        for tbl in soup.findAll("tbody", class_="mod-table_th-slim mod-table_td-slim"):
            for element in tbl.findAll("tr"):

                try:

                    response.meta['itm']['place_name'] = element.th.get_text().replace(' ','')
                
                    address = element.find("p", class_=None).get_text().replace('\n','').replace(' ','')
                    # print("ADDRESS:{}".format(address))
                    response.meta['itm']['address'] = address
    
                    url = element.find('p', class_='mod-button-link-single mt4').a.attrs['href']
                    # print('NOWURL:{}'.format(url))
                    if 'google' in url:
                        url = url.split('/@')[1].split('/')[0].split(',')[0:2]
                        # print('MAAAAAAAAAAAAP{}'.format(url))
                        response.meta['itm']['latitude'] = url[1]
                        response.meta['itm']['longitude'] = url[0]
    
                    else:
                        f = urlopen('http://www.yozemi.ac.jp' + url)
                        usp = BeautifulSoup(f, 'html.parser')
                        geo = usp.find("div", class_="school-information")\
                                .find('iframe').attrs['src'].split('!2d')[1].split('!3m2!')[0].split('!2m3!')[0].split('!3d')
                        # print('GEO:{}'.format(geo))
                        response.meta['itm']['latitude'] = geo[1]
                        response.meta['itm']['longitude'] = geo[0]
                    yield response.meta['itm']
                except:
                    print('some error occered in {}'.format(response.meta['itm']))
