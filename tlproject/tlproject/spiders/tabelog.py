import scrapy
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from tlproject.items import TLinfo
import time
import re

class TabelogSpider(scrapy.Spider):
    name = 'tabelog'
    allowed_domains = ['tabelog.com']
    start_urls = ['https://tabelog.com/']
    re_fig = re.compile("[*0-9]")

    def parse(self, response):

        soup = BeautifulSoup(response.body, 'html.parser')

        for top in soup.find_all(class_='rsttop-search__pref-list-item'):
            url = top.a.get('href')
            
            if 'tokyo' in url:
                print('URL:{} '.format(url))
                yield scrapy.Request((response.urljoin(url)), self.parse_all)

    def parse_all(self, response):

        soup = BeautifulSoup(response.body, 'html.parser')
        url = soup.find("div", class_="navi-count").a.get('href')
        print('ALL:{}'.format(url))
        yield scrapy.Request(response.urljoin(self.start_urls[0] + url), self.parse_area)

    def parse_area(self, response):

        soup = BeautifulSoup(response.body, 'html.parser')
        urls = soup.find("div", class_="area").ul
        for url in urls.find_all("li"):
            print('AREA:{}'.format(url.a.get('href')))
            yield scrapy.Request(response.urljoin(url.a.get('href')), self.parse_initial)

    def parse_initial(self, response):

        soup = BeautifulSoup(response.body, 'html.parser')
        urls = soup.find("div", class_="taglist").ul
        for url in urls.find_all("li"):
            print('INITIAL:{}'.format(url.a.get('href')))
            yield scrapy.Request(response.urljoin(url.a.get('href')), self.parse_rsname)

    def parse_rsname(self, response):

        soup = BeautifulSoup(response.body, 'html.parser')
        urls = soup.find_all("div", class_="rstname")
        for url in urls:
            # print('RSTNAME:{}'.format(url.a.get('href')))
            yield scrapy.Request(response.urljoin(url.a.get('href')), self.parse_location)

    def parse_pref(self, response):

        soup = BeautifulSoup(response.body, 'html.parser')

        for page in soup.find_all("a", class_="list-rst__rst-name-target cpy-rst-name"):
            yield scrapy.Request(response.urljoin(page.get('href')), self.parse_location)

        for url in soup.find_all("a", text="次の20件"):
            print('PRINT:{}'.format(url.get('href')))
            yield scrapy.Request(response.urljoin(url.get('href')), self.parse_pref)

    def parse_location(self, response):

        soup = BeautifulSoup(response.body, 'html.parser')

        item = TLinfo()
        item['url'] = response.url
        item['name'] = soup.h2.span.string.replace('\n', '').replace(' ', '')
        
        try:
            item['eval_point'] = soup.b.span.string
        except:
            item['eval_point'] = None
        
        try:
            item['eval_tex'] = self.parse_text_page(
                    soup.find("p", class_="rstdtl-top-rvwlst__more-link").a.get('href')
                    )
        except:
            item['eval_tex'] = []

        tbl = soup.find_all("table", class_="rstinfo-table__table")
        
        try:
            item['seats'] = tbl[1].p.string.replace("席","")
        except:
            item['seats'] = None
        
        try:
            budgets_dinner = soup\
                    .find("em", class_="gly-b-dinner").string.replace(",","").replace("￥","").split("～")
            if self.re_fig.match(budgets_dinner[0]):
                item['MAX_budget_dinner'] = budgets_dinner[1]
                item['MIN_budget_dinner'] = budgets_dinner[0]
            else:
                item['MAX_budget_dinner'] = None
                item['MIN_budget_dinner'] = None
        except:
            item['MAX_budget_dinner'] = None
            item['MIN_budget_dinner'] = None

        try:
            budgets_lunch = soup\
                    .find("em", class_="gly-b-lunch").string.replace(",","").replace("￥","").split("～")
            if self.re_fig.match(budgets_lunch[0]):
                item['MAX_budget_lunch'] = budgets_lunch[1]
                item['MIN_budget_lunch'] = budgets_lunch[0]
            else:
                item['MAX_budget_lunch'] = None
                item['MIN_bidget_lunch'] = None
        except:
            item['MAX_budget_lunch'] = None
            item['MIN_budget_lunch'] = None
        
        try:
            item['category'] = tbl[0].find_all("td")[1].span.string
        except:
            item['category'] = None

        try:
            item['address'] = tbl[0].find("p", class_="rstinfo-table__address").get_text()
        except:
            item['address'] = None

        try:
            latlon = tbl[0].find("img", class_="js-map-lazyload").get("data-original")
            latlon = latlon[latlon.find("center=")+7:latlon.find("&markers=color")].split(",")
            item['latitude'] = latlon[0]
            item['longitude'] = latlon[1]
        except:
            item['latitude'] = None
            item['longitude'] = None

        yield item

    def parse_text_page(self, url):
        comments = []
        driver = webdriver.PhantomJS()
        driver.get('https://' + self.allowed_domains[0] + url)
        time.sleep(1)
        tags = driver.find_elements_by_class_name('rvw-item__visit-contents')
        for tag in tags:
            try:
                a_tag = tag.find_elements_by_tag_name('a')
                a_tag[1].click()
            except:
                print("error:{}".format(tag))

        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for content in soup.find_all('div', class_="rvw-item js-rvw-item-clickable-area"):
            try:
                name = content\
                        .find('p', class_='rvw-item__rvwr-name auth-mobile').span.span.get_text()
            except:
                name = None

            try:
                age = None
                gender = None
                live_city = None
                for w in content.find('span', class_="rvw-item__rvwr-profile").string.split('・'):
                    if '0代' in w:
                        age = w
                    elif '男性' in w or '女性' in w:
                        gender = w
                    else:
                        live_city = w
            except:
                age = None
                gender = None
                live_city = None

            try:
                acnt = self.allowed_domains[0] \
                        + content.find('p', class_='rvw-item__rvwr-name auth-mobile').a.get('href')
            except:
                acnt = None

            try:
                date = content\
                        .find('div', class_='rvw-item__single-date').p\
                        .string.replace("\n", "").replace(" ", "").replace("訪問", "").split('/')
                year = date[0]
                month = date[1]
            except:
                year = None
                month = None
            #date = content.find('div', class_='rvw-item__single-date')

            try:
                ttl = content.find('p', class_='rvw-item__title').strong.get_text()
            except:
                ttl = None

            try:
                cmmnt = content.find('div', class_='rvw-item__rvw-comment').p.get_text().replace('\n', '')
            except:
                cmmnt = None
            
            try:
                price = content\
                        .find('strong', class_='c-rating__val rvw-item__usedprice-price')\
                        .string.replace('￥', '').replace(',', '').split('～')
                max_price = price[1]
                min_price = price[0]
                if not self.re_fig.match(max_price):
                    max_price = None
                if not self.re_fig.match(min_price):
                    min_price = None
            except:
                max_price = None
                min_price = None

            try:
                dinner = content\
                        .find('span', class_='c-rating__time c-rating__time--dinner')
                lunch = content\
                        .find('span', class_='c-rating__time c-rating__time--lunch')
                if dinner:
                    timing = dinner.string.replace('の点数：', '')
                elif lunch:
                    timing = lunch.string.replace('の点数：', '')
            except:
                timing = None

            try:
                score = content\
                        .find('b', class_="c-rating__val c-rating__val--strong").string.replace(',','')
                if not self.re_fig.match(score):
                    score = None
            except:
                score = None
                
            try:
                logs = content\
                        .find_all('span', class_="rvw-item__rvwr-balloon-text")[0]\
                        .string.replace('ログ', '').replace(',', '')
                if not self.re_fig.match(logs):
                    logs = None
            except:
                logs = None

            try:
                fllwr = content\
                        .find('span', class_='rvw-item__rvwr-rvwcount count')\
                        .string.replace('(', '').replace(')', '').replace(',', '')
                if not self.re_fig.match(fllwr):
                    fllwr = None
            except:
                fllwr = None

            try:
                fllwng = content\
                        .find_all('span', class_="rvw-item__rvwr-balloon-text")[1]\
                        .string.replace('フォロー', '').replace('人', '').replace(',', '')
                if not self.re_fig.match(fllwng):
                    fllwng = None
            except:
                fllwing = None

            comments.append(
                    { 
                        'user_name':name,
                        'user_url':acnt,
                        'user_age':age,
                        'user_gender':gender,
                        'user_live_city':live_city,
                        'year':year,
                        'month':month,
                        'title':ttl, 
                        'comment':cmmnt, 
                        'max_price':max_price, 
                        'min_price':min_price, 
                        'timing':timing, 
                        'score':score, 
                        'log_cnt':logs, 
                        'follower_cnt':fllwr, 
                        'following_cnt':fllwng,
                    }
                )
        #except:
        #    print('LOSE DATA Some Error happen.')

        next_url = driver.find_elements_by_class_name("c-pagination__item")
        if next_url:
            next_url = next_url[-1].find_element_by_css_selector('a').get_attribute('href') 
            print('go next comment page')
        else:
            print('all comments crawled')

        driver.quit()
        return comments
