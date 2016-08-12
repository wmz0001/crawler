import scrapy


class UserItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    location = scrapy.Field()
    business = scrapy.Field()
    gender = scrapy.Field()
    education = scrapy.Field()
    employment = scrapy.Field()
    ask = scrapy.Field()
    answer = scrapy.Field()
    agree = scrapy.Field()
    thanks = scrapy.Field()
