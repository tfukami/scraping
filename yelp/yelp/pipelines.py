# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import os

class YelpPipeline(object):
    def process_item(self, item, spider):
        return item


class MySQLPipeLine(object):

    def open_spider(self, spider):
        settings = spider.settings
        params = {
                'host': settings.get('MYSQL_HOST', 'localhost'),
                'db': settings.get('MYSQL_DATABASE', 'yelp'),
                'user': settings.get('MYSQL_USER', 'data_writer'),
                'passwd': settings.get('MYSQL_PASSWORD', os.environ.get('MYSQL_PASSWORD')),
                'charset': settings.get('MYSQL_CHARSET', 'utf8mb4'),
            }

        self.conn = MySQLdb.connect(**params)
        self.c = self.conn.cursor()
        self.c.execute('''
            create table if not exists retail_data (
                id integer not null auto_increment,
                url varchar(1000),
                name varchar(255),
                jp_name varchar(255),
                rating varchar(100),
                review_cnt varchar(100),
                price varchar(255),
                address varchar(255),
                latitude double,
                longitude double,
                primary key (id)
            )
            ''')
        self.conn.commit()


    def close_spider(self, spider):
        self.conn.close()


    def process_item(self, item, spider):
        if not item['url']:
            raise DropItem('No URL Data : {}'.format(item))
        check_sql = \
                'select url from retail_data where url = "{}"'\
                .format(item['url'])
        print('CHECK_SQL : {}'.format(check_sql))
        self.c.execute(check_sql)
        self.conn.commit()

        if self.c.fetchall():
            print('Item has already exists in db')
        else:
            sql_insert = "insert into retail_data (\
                    url, \
                    name, \
                    jp_name, \
                    rating, \
                    review_cnt, \
                    price, \
                    address, \
                    latitude, \
                    longitude) \
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"

            insert_item = (
                    item['url'],
                    item['name'],
                    item['jp_name'],
                    item['rating'],
                    item['review_cnt'],
                    item['price'],
                    item['address'],
                    item['latitude'],
                    item['longitude'],
                    )

            self.c.execute(sql_insert, insert_item)
            self.conn.commit()
            print('New Item inserted!')

        return item
