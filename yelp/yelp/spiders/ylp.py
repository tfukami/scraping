import scrapy
from logging import getLogger,Formatter,StreamHandler,FileHandler,DEBUG
#from scrapy_splash import SplashRequest

from bs4 import BeautifulSoup
from urllib.request import urlopen
from yelp.items import YPInfo
import urllib
import re


class YlpSpider(scrapy.Spider):
    name = 'ylp'
    allowed_domains = ['yelp.com']
    start_urls = [\
            'https://www.yelp.com/search?find_desc=&find_loc=Tokyo%2C+{}%2C+Japan&ns=1'\
            .format(urllib.parse.quote("東京都"))\
            ]
    re_fig = re.compile("[*0-9]")
    url_head = 'https://www.yelp.com'

    logger = getLogger('LOG:')
    formatter = Formatter\
            ('%(asctime)s [%(levelname)s] [%(filename)s: \
            %(funcName)s: %(lineno)d] %(message)s')
    handlerSh = StreamHandler()
    handlerFile = FileHandler('error.log')
    handlerSh.setFormatter(formatter)
    handlerSh.setLevel(DEBUG)
    handlerFile.setLevel(DEBUG)
    handlerFile.setFormatter(formatter)
    logger.setLevel(DEBUG)
    logger.addHandler(handlerSh)
    logger.addHandler(handlerFile)
    logger.debug('log start')


#    def start_requests(self):
#        for url in self.start_urls:
#            # self.logger.debug('strat url:{}'.format(url))
#            yield SplashRequest(url, self.parse,
#                    args={'wait': 1.0},
#                    )


    # 店舗へのリンク集
    def parse(self, response):
        # self.logger.debug('RESPONSE URL:{}'.format(response.url))
        for url in response.xpath('//a[@class="biz-name js-analytics-click"]/@href'):
#            yield SplashRequest(self.url_head+url.extract(), self.parse_page)
            yield scrapy.Request(self.url_head+url.extract(), self.parse_page)
            self.logger.debug('URL:{}'.format(url.extract()))

        next_url = \
                response.xpath(\
                '//a[@class="u-decoration-none next pagination-links_anchor"]/@href'\
                )[0].extract()
        # self.logger.debug('next_url:{}'.format(next_url))
        # next page
        if next_url:
            # self.logger.debug('next_url:{}'.format('https://www.yelp.com' + next_url))
#            yield SplashRequest(self.url_head+next_url, self.parse)
            yield scrapy.Request(self.url_head+next_url, self.parse)


    # 個別ページ
    def parse_page(self, response):
        item = YPInfo()

        try:
            item['url'] = response.url
        except:
            self.logger.warning('There is no url in {}'.format(response))
            item['url'] = None

        try:
            item['name'] = response.xpath(\
                    '//h1[@class="biz-page-title embossed-text-white shortenough"]/text()'\
                    )[0].extract().replace('\n','').replace('  ','')
        except:
            try:
                item['name'] = response.xpath(\
                        '//h1[@class="biz-page-title embossed-text-white"]/text()'\
                        )[0].extract().replace('\n','').replace('  ','')
            except:
                self.logger.warning('There is no name in {}'.format(response))
                item['name'] = None

        try:
            item['jp_name'] = response.xpath(\
                    '//div[@class="alternate-names h3 alternate"]/text()'\
                    )[0].extract().replace('\n','').replace('  ','') 
        except:
            self.logger.warning('There is no jp_name in {}'.format(response))
            item['jp_name'] = None

        try:
            item['rating'] = response.xpath(\
                    '//div[@class="biz-rating biz-rating-very-large clearfix"]/div/@title'\
                    )[0].extract().replace('\n','').replace('  ','') 
        except:
            self.logger.warning('There is no rating score in {}'.format(response))
            item['rating'] = None

        try:
            item['category'] = response.xpath(\
                    '//span[@class="category-str-list"]/a/text()'\
                    )[0].extract().replace('\n','').replace('  ','')
        except:
            self.logger.warning('There is no category in {}'.format(response))
            item['category'] = None

        try:
            item['review_cnt'] = response.xpath(\
                    '//span[@class="review-count rating-qualifier"]/text()'\
                    )[0].extract().replace('\n','').replace('  ','') 
        except:
            self.logger.warning('There is no review_cnt in {}'.format(response))
            item['review_cnt'] = None

        try:
            geo = response.xpath(\
                    '//img[@alt="Map"]/@src'
                    )[0].extract()
            geo = geo.split('center=')[1].split('&language')[0].split('%2C')
            item['latitude'] = geo[0]
            item['longitude'] = geo[1]
        except:
            self.logger.warning('There in no geo_info in {}'.format(response))
            item['latitude'] = None
            item['longitude'] = None

        try:
            addrss = ''
            for ad in response.xpath('//strong[@class="street-address"]/address/text()'):
                    addrss += ad.extract().replace('\n','').replace('  ','').replace(',','')
            item['address'] = addrss
#            item['address'] = response.xpath(\
#                    '//strong[@class="street-address"]/address/text()'
#                    )[0].extract().replace('\n','').replace('  ','') 
        except:
            self.logger.warning('There is no address in {}'.format(response))
            item['address'] = None

        try:
            item['price'] = response.xpath(\
                    '//dd[@class="nowrap price-description"]/text()'
                    )[0].extract().replace('\n','').replace('  ','') 
        except:
            self.logger.warning('There is no price in {}'.format(response))
            item['price'] = None

        return item
