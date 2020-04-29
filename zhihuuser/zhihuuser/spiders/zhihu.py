# -*- coding: utf-8 -*-
from scrapy import Request,Spider
import json
from zhihuuser.items import UserItem
from time import sleep

class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']

    start_user = 'excited-vczh' # 轮子哥

    user_url = 'https://www.zhihu.com/people/{user}/'
    followees_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={offset}&limit={limit}'

    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user), callback=self.parse_user)
        # yield Request(self.followees_url.format(user=self.start_user, offset=0, limit=20), callback=self.parse_follows)

    def parse_user(self, response):
        response_json = response.css('#js-initialData::text').extract_first()
        users = json.loads(response_json)['initialState']['entities']['users']
        infos = users.items()
        for key, value in infos: # 其实就一个用户，放在了字典中
            yield self.parse_user_info(value)
            yield Request(self.followees_url.format(user=value['urlToken'], offset=0, limit=20), callback=self.parse_follows)

    def parse_user_info(self, info):
        item = UserItem()
        for field in item.fields:
            if field in info.keys():
                item[field] = info.get(field)
        return item

    def parse_follows(self, response):
        response_json = json.loads(response.text)
        data = response_json['data']
        for follows_info in data:
            if follows_info['follower_count'] > 100000: # 爬取关注数>100000的用户
                sleep(1)
                yield Request(self.user_url.format(user=follows_info['url_token']), callback=self.parse_user)

        is_page_end = response_json['paging']['is_end']
        if is_page_end is False:
            sleep(1)
            yield Request(response_json['paging']['next'], callback=self.parse_follows)