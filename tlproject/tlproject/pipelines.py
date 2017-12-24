# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import os

class TlprojectPipeline(object):
    def process_item(self, item, spider):
        return item

class MySQLPipeLine(object):

    def open_spider(self, spider):
        settings = spider.settings
        params = {
                'host': settings.get('MYSQL_HOST', 'localhost'),
                'db': settings.get('MYSQL_DATABASE', 'tabelog'),
                'user': settings.get('MYSQL_USER', 'data_writer'),
                'passwd': settings.get('MYSQL_PASSWORD', os.environ.get('MYSQL_PASSWORD')),
                'charset': settings.get('MYSQL_CHARSET', 'utf8mb4'),
            }

        self.conn = MySQLdb.connect(**params)
        self.c = self.conn.cursor()
        self.c.execute('''
            create table if not exists raw_data (
                id integer not null auto_increment,
                url varchar(255),
                name varchar(255),
                eval_point float,
                MAX_budget_dinner integer,
                MIN_budget_dinner integer,
                MAX_budget_lunch integer,
                MIN_budget_lunch integer,
                seats integer,
                category varchar(255),
                address varchar(255),
                latitude double,
                longitude double,
                primary key (id)
            )
            ''')
        self.conn.commit()

        self.c.execute('''
            create table if not exists raw_comments_data (
                id integer not null auto_increment,
                name varchar(100),
                url varchar(255),
                year integer,
                month integer,
                latitude double,
                longitude double,
                user_name varchar(100),
                user_age varchar(10),
                user_gender varchar(5),
                user_live_city varchar(255),
                title varchar(100),
                comment varchar(10000),
                max_price integer,
                min_price integer,
                timing char(10),
                log_cnt integer,
                follower_cnt integer,
                following_cnt integer,
                primary key (id)
            )
        ''')
        self.conn.commit()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        sql_insert = "insert into raw_data (\
                url, \
                name, \
                eval_point, \
                MAX_budget_dinner, \
                MIN_budget_dinner, \
                MAX_budget_lunch, \
                MIN_budget_lunch, \
                seats, \
                category, \
                address, \
                latitude, \
                longitude) \
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        insert_item = (
                item['url'],
                item['name'], 
                item['eval_point'],
                item['MAX_budget_dinner'],
                item['MIN_budget_dinner'],
                item['MAX_budget_lunch'],
                item['MIN_budget_lunch'],
                item['seats'],
                item['category'],
                item['address'],
                item['latitude'],
                item['longitude'],
                )
        try:
            self.c.execute(sql_insert, insert_item)
            self.conn.commit()
        except:
            print('some error happen in {}'.format(insert_item))
        for cmmnt in item['eval_tex']:
            cmmnt_insert = "insert into raw_comments_data (\
                    name, \
                    url, \
                    year, \
                    month, \
                    latitude, \
                    longitude, \
                    user_name, \
                    user_age, \
                    user_gender, \
                    user_live_city, \
                    title, \
                    comment, \
                    max_price, \
                    min_price, \
                    timing, \
                    log_cnt, \
                    follower_cnt, \
                    following_cnt) \
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
                    %s, %s, %s, %s, %s, %s, %s, %s)"
            cmmnt_item = (
                    item['name'],
                    item['url'],
                    cmmnt['year'],
                    cmmnt['month'],
                    item['latitude'],
                    item['longitude'],
                    cmmnt['user_name'],
                    cmmnt['user_age'],
                    cmmnt['user_gender'],
                    cmmnt['user_live_city'],
                    cmmnt['title'],
                    cmmnt['comment'],
                    cmmnt['max_price'],
                    cmmnt['min_price'],
                    cmmnt['timing'],
                    cmmnt['log_cnt'],
                    cmmnt['follower_cnt'],
                    cmmnt['following_cnt'],
                    )
            try:
                self.c.execute(cmmnt_insert, cmmnt_item)
                self.conn.commit()
            except:
                print('some error happen in comments {}'.format(cmmnt_item))
        return item
