# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import os

class JukucrawlPipeline(object):
    def process_item(self, item, spider):
        return item

class YoyogiMoshiPipeline(object):
    def open_spider(self, spider):
        settings = spider.settings
        params = {
                'host' : settings.get('MYSQL_HOST', 'localhost'),
                'db' : settings.get('MYSQL_DATABASE', 'juku'),
                'user' : settings.get('MYSQL_USER', 'data_writer'),
                'passwd' : settings.get('MYSQL_PASSWORD', os.environ.get('MYSQL_PASSWORD')),
                'charset' : settings.get('MYSQL_CHARSET', 'utf8mb4'),
            }

        self.conn = MySQLdb.connect(**params)
        self.c = self.conn.cursor()
        self.c.execute('''
            create table if not exists yoyogi (
                id integer not null auto_increment,
                grade varchar(100),
                name varchar(100),
                place_name varchar(50),
                date varchar(100),
                address varchar(255),
                latitude double,
                longitude double,
                primary key(id)
            )
            ''')
        self.conn.commit()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        sql_insert = "insert into yoyogi (\
                grade, \
                name, \
                place_name, \
                date, \
                address, \
                latitude, \
                longitude) \
                values (%s,%s,%s,%s,%s,%s,%s)"
        insert_item = (
                item['grade'],
                item['name'],
                item['place_name'],
                item['date'],
                item['address'],
                item['latitude'],
                item['longitude'])
        self.c.execute(sql_insert, insert_item)
        self.conn.commit()
