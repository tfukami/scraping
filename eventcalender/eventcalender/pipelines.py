# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import os


class EventcalenderPipeline(object):
    def open_spider(self, spider):
        settings = spider.settings
        params = {
                'host' : settings.get('MYSQ_HOST', 'localhost'),
                'db' : settings.get('MYSQL_DATABASE', 'event_calender'),
                'user' : settings.get('MYSQL_USER', 'data_writer'),
                'passwd' : settings.get('MYSQL_PASSWORD', os.environ.get('MYSQL_PASSWORD')),
                'charset' : settings.get('MYSQL_CHARSET', 'utf8mb4'),
                }
        self.conn = MySQLdb.connect(**params)
        self.c = self.conn.cursor()
        self.c.execute('''
            create table if not exists raw_data (
                id integer not null auto_increment,
                name varchar(255),
                start_at timestamp,
                place varchar(100),
                url varchar(255),
                primary key(id)
            )
            ''')
        self.conn.commit()


    def close_spider(self, spider):
        self.conn.close()


    def process_item(self, item, spider):
        sql_insert = "insert into raw_data (\
                name, \
                start_at, \
                place, \
                url) \
                values (%s,%s,%s,%s)"
        insert_item = (
                item['name'],
                item['start_at'],
                item['place'],
                item['url']
                )
        self.c.execute(sql_insert, insert_item)
        self.conn.commit()
        return item
