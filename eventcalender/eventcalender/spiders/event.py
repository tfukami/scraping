import scrapy
from logging import getLogger, Formatter, StreamHandler, FileHandler, DEBUG
from bs4 import BeautifulSoup
from eventcalender.items import EVinfo
import re

class EventSpider(scrapy.Spider):
    name = 'event'
    allowed_domains = ['live-events.a-jp.org']
    start_urls = ['http://live-events.a-jp.org/soko/cld/']

    logger = getLogger('dev-info')
    formatter = Formatter\
            ('%(asctime)s [%(levelname)s [%(filename)s: \
            %(funcName)s: %(lineno)d] %(message)s')
    handlerSh = StreamHandler()
    handlerFile = FileHandler('error.log')
    handlerSh.setLevel(DEBUG)
    handlerFile.setLevel(DEBUG)
    handlerFile.setFormatter(formatter)
    logger.setLevel(DEBUG)
    logger.addHandler(handlerSh)
    logger.addHandler(handlerFile)
    logger.debug('logging start')


    def parse(self, response):

        soup = BeautifulSoup(response.body, 'html.parser')

        for url in soup.find('table', id='table82').find_all('a'):
            self.logger.debug(url.get('href'))
            yield scrapy.Request((response.urljoin(url.get('href'))), self.parse_event)


    def parse_event(self, response):
        
        soup = BeautifulSoup(response.body, 'html.parser')

        for urls in soup.find('table', id='table1').find_all('a'):
            url = urls.get('href')
            self.logger.debug(urls.get_text())
            self.logger.debug(urls.get('href'))
            # self.logger.debug(urls.get('href').find_next('td').get_text())
            if url and 'http://live-events.a-jp.org/soko/p/' not in url:
                item = EVinfo()
                item['url'] = url
                item['name'] = urls.get_text()
                item['place'] = urls.find_next('td').get_text()
                self.logger.debug(urls.find_next('td').get_text())
                req = scrapy.Request(response.urljoin(url), self.parse_items)
                req.meta['itm'] = item
                yield req


    def parse_items(self, response):

        soup = BeautifulSoup(response.body, 'html.parser')

        self.logger.debug('PURL:{}'.format(response.meta['itm']['url']))
        for c in soup.find('table', id='table88').get_text().split('\n'):
            if ('開場' in c or '開演' in c) and '年' in c and '20' in c and ':' in c:
                y = c.replace(' ','').replace('　','').replace('年','-').replace('/','-')
                y = re.split('[(（]', y)
                d = y[0] + ' ' + re.split('[)）]', y[1])[1]
                if '開場' in d:
                    d = d.split('開場')[0]
                elif '開演' in d:
                    d = d.split('開演')[0]
                self.logger.debug(d)
                response.meta['itm']['start_at'] = d
                
                yield response.meta['itm']
