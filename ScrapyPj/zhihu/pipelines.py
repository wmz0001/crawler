import sys
import MySQLdb
import hashlib
from scrapy.exceptions import NotConfigured
from scrapy.exceptions import DropItem
from scrapy.http import Request

from zhihu.myconfig import DbConfig
from zhihu.items import UserItem


class UserPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect(user=DbConfig['user'], passwd=DbConfig['passwd'], db=DbConfig['db'],
                                    host=DbConfig['host'], charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            self.cursor.execute(
                """INSERT IGNORE INTO user (url, location, business, gender, education, employment, ask, answer, agree, thanks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    item['url'],
                    item['location'],
                    item['business'],
                    item['gender'],
                    item['education'],
                    item['employment'],
                    item['ask'],
                    item['answer'],
                    item['agree'],
                    item['thanks'],
                )
            )
            self.conn.commit()
        except MySQLdb.Error, e:
            print
            'Error %d %s' % (e.args[0], e.args[1])

        return item
