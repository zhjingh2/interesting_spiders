# -*- coding: utf-8 -*-
import scrapy
from mzitu.items import MzituItem
import re
import time

MZITU_ALL_NEW = 'https://www.mzitu.com/all/'
MZITU_ALL_OLD = 'https://www.mzitu.com/old/'


class MzituallSpider(scrapy.Spider):
    name = 'mzituall'
    allowed_domains = ['www.mzitu.com']
    start_urls = [MZITU_ALL_NEW, MZITU_ALL_OLD]

    def parse(self, response):
        url_a_list = response.css('body > div.main > div.main-content > div.all > ul > li > p.url > a')
        self.logger.debug('url_list count: ' + str(len(url_a_list.extract())))
        db = self.myPipeline.get_db()
        for detail_a_url in url_a_list:
            real_url = detail_a_url.css('::attr(href)').extract_first()
            m = detail_a_url.xpath('../../p[@class="month"]/em/text()').extract_first()
            y = detail_a_url.xpath('../../../../div[@class="year"]/text()').extract_first()
            month_key = y.replace("年", "") + '-' + m.replace("月", "")
            exist = db[month_key].find_one({'url': real_url})
            if exist != None:
                self.logger.debug('item has exist: ' + month_key + ' ' + real_url)
                continue

            time.sleep(0.5)
            yield scrapy.Request(url=real_url, callback=self.detail_parse)

    def detail_parse(self, response):
        item = MzituItem()
        date_str = response.css('body > div.main > div.content > div.main-meta > span:nth-child(2)').extract_first()
        item['month'] = re.search(' (\d{4}-\d{2})-\d{2} ', date_str).group(1)
        item['date'] = re.search(' (\d{4}-\d{2}-\d{2}) ', date_str).group(1)
        item['title'] = response.css('body > div.main > div.content > h2::text').extract_first()
        item['url'] = response.url
        item['type'] = response.css('body > div.main > div.content > div.main-meta > span:nth-child(1) > a::text').extract_first()
        item['tags'] = ' '.join(response.css('body > div.main > div.content > div.main-tags > a::text').extract())
        return item