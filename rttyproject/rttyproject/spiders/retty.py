import scrapy
from scrapy_splash import SplashRequest

from bs4 import BeautifulSoup
from urllib.request import urlopen
from rttyproject.items import RTinfo
import re

class RettySpider(scrapy.Spider):
    name = 'retty'
    allowed_domains = ['retty.me']
    start_urls = ['https://retty.me']
    re_fig = re.compile("[*0-9]")

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                    args={'wait': 1.0},
                    )

    def parse(self, response):
        # 地域ごとにurl取得
        for l in response.xpath('//section[@is="area-detail"]').extract():
            meta = l.split(":parent=")[1].split(':children="[')
            children = meta[1].replace("]","").replace("{","").replace(" ", "").replace("\n","").split("},")
            # 都道府県ごとのurl取得
            for child in children[0:-1]:
                url = child.split("url:'")[1].replace("'", "")
                # if url == 'https://retty.me/area/PRE10/ARE545/':
                yield SplashRequest(url, self.parse_pref)

    def parse_pref(self, response):
        # 詳細page取得
        for url in response\
                .xpath('//div[@class="table-box__main"]/h3/a[@class="js-log-action"]/@href').extract():
            yield SplashRequest(url, self.parse_location)
        
        # Nextpage取得
        next_url = response\
                .xpath('//ul[@class="pagination pagination-long"]/li[@class="active"]\
                /following-sibling::li[1]/a/@href').extract()
        if next_url:
            yield SplashRequest(url, self.parse_pref)

    def parse_location(self, response):
        # 詳細店舗pagaからの取得
        item = RTinfo()
        
        # print('URL:{}'.format(response.url))
        item['url'] = response.url
        
        try:
            name = response.xpath('//p[@class="font-md bold"]/text()').extract()
            if name:
                name = name[0]
            else:
                name = None
        except:
            name = None
        item['name'] = name

        try:
            eval_point = response.xpath('//span[@class="u-font-big u-font-bold"]/text()').extract()
            if eval_point:
                eval_point = eval_point[0].replace('%', '')
            else:
                eval_point = None
        except:
            eval_point = None
        item['eval_point'] = eval_point

        try:
            visiter = response.xpath('//span[@class="balloon__number"]/text()').extract()
        except:
            visiter = None
        if not visiter:
            visiter = [0, 0]

        visited = visiter[0]
        # print('VISITED:{}'.format(visited))
        item['visited'] = visited

        wanna_visit = visiter[1]
        # print('WANNA_VISIT:{}'.format(wanna_visit))
        item['wanna_visit'] = wanna_visit

        try:
            budget = response\
                    .xpath('//span[@itemprop="priceRange"]/p[@class="overview__info-cat"]/text()').extract()
            if '～' in budget[1]:
                l_budget = budget[1].replace('\n', '').replace(' ', '').replace('円', '').split('～')
                MAX_budget_lunch = l_budget[1]
                MIN_budget_lunch = l_budget[0]
                if not self.re_fig.match(MAX_budget_lunch):
                    MAX_budget_lunch = None
                if not self.re_fig.match(MIN_budget_lunch):
                    MIN_budget_lunch = None
            else:
                MAX_budget_lunch = None
                MIN_budget_lunch = None
            if '～' in budget[2]:
                d_budget = budget[2].replace('\n', '').replace(' ', '').replace('円', '').split('～')
                MAX_budget_dinner = d_budget[1]
                MIN_budget_dinner = d_budget[0]
                if not self.re_fig.match(MAX_budget_dinner):
                    MAX_budget_dinner = None
                if not self.re_fig.match(MIN_budget_dinner):
                    MIN_budget_dinner = None
            else:
                MAX_budget_dinner = None
                MIN_budget_dinner = None
        except:
            MAX_budget_lunch = None
            MIN_budget_lunch = None
            MAX_budget_dinner = None
            MIN_budget_dinner = None
        item['MAX_budget_dinner'] = MAX_budget_dinner
        item['MIN_budget_dinner'] = MIN_budget_dinner
        item['MAX_budget_lunch'] = MAX_budget_lunch
        item['MIN_budget_lunch'] = MIN_budget_lunch

        try:
            seats = response\
                .xpath('//table[@class="table table-type-1"]/tbody/tr/th[contains(text(), "座席")]/\
                following-sibling::td[1]/text()').extract()
            if seats:
                seats = seats[0].replace('席', '').replace(' ','').replace('\n','')
            else:
                seats = None
        except:
            seats = None
        item['seats'] = seats

        try:
            area = response.xpath('//p[@class="font-s head_info_address"]/span/text()').extract()
            address = ''
            for i in area[1:]:
                address += i
        except:
            address = None
        item['address'] = address

        try:
            created_at = response\
                .xpath('//span[@itemprop="dateModified" and @class="date"]/text()').extract()
            if created_at:
                created_at = created_at[0].replace("年","-").replace("月","-").replace("日", "")
            else:
                created_at = None
        except:
            created_at = None
        item['created_at'] = created_at

        try:
            latitude = response.xpath('//meta[@itemprop="latitude"]/@content').extract_first()
            longitude = response.xpath('//meta[@itemprop="longitude"]/@content').extract_first()
        except:
            latitude = None
            longitude = None
        item['latitude'] = latitude
        item['longitude'] = longitude

        try:
            category = response.xpath('//span[@itemprop="servesCuisine"]/text()').extract()
            if category:
                category = category[0]
            else:
                category = None
        except:
            category = None
        item['category'] = category

        try:
            eval_tex = response.xpath('//ul[@class="list list-vert-1" and @itemtype="http://schema.org/ItemList"]')
            item['eval_tex'] = self.parser_detail_comment(response)
        except:
            item['eval_tex'] = None
        
        yield item


    def parser_detail_comment(self, obj):
        cmmnts = []
        
        soup = BeautifulSoup(obj.body, 'html.parser')
        
        url = obj.url
        try:
            name = soup\
                    .find("span", class_="overview__name l-height-xs", itemprop="name")\
                    .get_text().replace("\n","")
        except:
            name = None

        for dat in soup.find_all("ul", class_='list list-vert-1', itemtype="http://schema.org/ItemList"):
            
            try:
                user_name = dat.find("span", class_="bold", itemprop="author")\
                        .get_text().replace("\n","")
            except:
                user_name = None

            try:
                timing = dat.find("span", class_="ml5 black-sm font-xs")\
                        .get_text().replace("\n","")
            except:
                timing = None

            try:
                created_at = dat.find("span", itemprop="datePublished")\
                        .get_text().replace("年","-").replace("月","-").replace("日", "")
            except:
                created_at = None

            try:
                EVAL = dat.find("meta", itemprop="ratingValue").get("content")
            except:
                EVAL = None

            try:
                text = dat.find("span", itemprop="reviewBody").get_text().replace("\n","")
            except:
                text = None

            cmmnts.append(
                    {
                        'name':name,
                        'url':url,
                        'user_name':user_name,
                        'timing':timing,
                        'created_at':created_at,
                        'eval':EVAL,
                        'text':text,
                        }
                    )

        return cmmnts
