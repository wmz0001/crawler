import os
import time

from zhihu.myconfig import UsersConfig

import scrapy
from zhihu.items import UserItem


class UsersSpider(scrapy.Spider):
    name = 'users'
    allowed_domains = ["zhihu.com"]
    domain = 'https://www.zhihu.com'
    login_url = 'https://www.zhihu.com/login/phone_num'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Host": "www.zhihu.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36"
    }

    def __init__(self, url="https://www.zhihu.com/people/excited-vczh"):
        self.user_url = url

    def start_requests(self):
        print
        'start_request'
        yield scrapy.Request(
            url=self.domain + "/#signin",
            headers=self.headers,
            meta={
                'cookiejar': 1
            },
            callback=self.request_captcha,
            dont_filter=True
        )

    def post_login(self, response):
        _xsrf = response.css('input[name="_xsrf"]::attr(value)').extract()[0]
        yield scrapy.FormRequest(
            url=self.login_url,
            headers=self.headers,
            formdata={
                'phone_num': UsersConfig['account'],
                'password': UsersConfig['password'],
                '_xsrf': _xsrf,
                'remember_me': 'true',
                'captcha': "cn"
            },
            meta={
                'cookiejar': response.meta['cookiejar']
            },
            callback=self.islogin,
            dont_filter=True
        )

    def login(self, response):
        yield scrapy.Request(
            url=self.domain + "/#signin",
            headers=self.headers,
            meta={
                'cookiejar': response.meta['cookiejar']
            },
            callback=self.request_zhihu,
            dont_filter=True
        )

    # def request(self, response):
    #     yield scrapy.Request(
    #         url=self.user_url + '/about',
    #         headers=self.headers,
    #         meta={
    #             'cookiejar': response.meta['cookiejar'],
    #         },
    #         callback=self.islogin,
    #     )

    # def islogin(self, response):
    #     filename = response.url.split("/")[-2]
    #     open(filename, 'wb').write(response.body)

    def request_captcha(self, response):
        _xsrf = response.css('input[name="_xsrf"]::attr(value)').extract()[0]
        captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + str(time.time() * 1000) + "&type=login"
        yield scrapy.Request(
            url=captcha_url,
            headers=self.headers,
            meta={
                'cookiejar': response.meta['cookiejar'],
                '_xsrf': _xsrf
            },
            callback=self.download_captcha,
            dont_filter=True
        )

    def download_captcha(self, response):
        with open('captcha.gif', 'wb') as fp:
            fp.write(response.body)
        os.system('start captcha.gif')
        print
        'Please enter captcha: '
        captcha = raw_input()

        yield scrapy.FormRequest(
            url=self.login_url,
            headers=self.headers,
            formdata={
                'phone_num': UsersConfig['account'],
                'password': UsersConfig['password'],
                '_xsrf': response.meta['_xsrf'],
                'remember_me': 'true',
                'captcha': captcha
            },
            meta={
                'cookiejar': response.meta['cookiejar']
            },
            callback=self.login,
            dont_filter=True
        )

    def request_zhihu(self, response):
        yield scrapy.Request(
            url=self.user_url + '/about',
            headers=self.headers,
            meta={
                'cookiejar': response.meta['cookiejar'],
            },
            callback=self.user_item,
        )

        yield scrapy.Request(
            url=self.user_url + '/followees',
            headers=self.headers,
            meta={
                'cookiejar': response.meta['cookiejar'],
            },
            callback=self.user_start,
        )

        yield scrapy.Request(
            url=self.user_url + '/followers',
            headers=self.headers,
            meta={
                'cookiejar': response.meta['cookiejar'],
            },
            callback=self.user_start,
        )

    def user_start(self, response):
        sel_root = response.xpath('//h2[@class="zm-list-content-title"]')
        if len(sel_root):
            for sel in sel_root:
                people_url = sel.xpath('a/@href').extract()[0]

                yield scrapy.Request(
                    url=people_url + '/about',
                    headers=self.headers,
                    meta={
                        'cookiejar': response.meta['cookiejar'],
                    },
                    callback=self.user_item,
                )

                yield scrapy.Request(
                    url=people_url + '/followees',
                    headers=self.headers,
                    meta={
                        'cookiejar': response.meta['cookiejar'],
                    },
                    callback=self.user_start,
                )

                yield scrapy.Request(
                    url=people_url + '/followers',
                    headers=self.headers,
                    meta={
                        'cookiejar': response.meta['cookiejar'],
                    },
                    callback=self.user_start,
                )

    def user_item(self, response):
        def value(list):
            return list[0] if len(list) else ''

        sel = response.xpath('//div[@class="zm-profile-header ProfileCard"]')

        item = UserItem()
        item['url'] = response.url[29:-6]
        item['location'] = value(sel.xpath('//span[contains(@class, "location")]/@title').extract()).encode('utf-8')
        item['business'] = value(sel.xpath('//span[contains(@class, "business")]/@title').extract()).encode('utf-8')
        item['gender'] = 0 if sel.xpath('//i[contains(@class, "icon-profile-female")]') else 1
        item['education'] = value(sel.xpath('//span[contains(@class, "education")]/@title').extract()).encode('utf-8')
        item['employment'] = value(sel.xpath('//span[contains(@class, "employment")]/@title').extract()).encode('utf-8')
        item['ask'] = int(
            sel.xpath('//div[contains(@class, "profile-navbar")]/a[2]/span[@class="num"]/text()').extract()[0])
        item['answer'] = int(
            sel.xpath('//div[contains(@class, "profile-navbar")]/a[3]/span[@class="num"]/text()').extract()[0])
        item['agree'] = int(sel.xpath('//span[@class="zm-profile-header-user-agree"]/strong/text()').extract()[0])
        item['thanks'] = int(sel.xpath('//span[@class="zm-profile-header-user-thanks"]/strong/text()').extract()[0])

        yield item
