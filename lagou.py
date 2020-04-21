from selenium import webdriver
from pyquery import PyQuery as pq
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
import pymongo

LOGIN_ACCOUNT = '15521105971'
LOGIN_SECRET = 'zhangjinghao'
PRE_LOGIN_URL = 'https://www.lagou.com/guangzhou/'
KEY_WORD = '运营'
SEARCH_URL = 'https://www.lagou.com/jobs/list_'

MONGO_URL = 'localhost'
MONGO_DB = 'lagou'
MONGO_COLLECTION = KEY_WORD

class Handler(object):
    crawl_config = {
    }

    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 20)
    client = pymongo.MongoClient(MONGO_URL)
    db = client[MONGO_DB]

    def on_start(self):
        self.login_in()
        start_url = self.create_search_url()
        self.crawl(start_url)

    def login_in(self):
        self.browser.get(PRE_LOGIN_URL)

        login_entrance = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="lg_tbar"]/div/div[2]/ul/li[3]/a')))
        login_entrance.click()
        account_input = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[1]/div/div[1]/form/div[1]/div/input')))
        account_input.clear()
        account_input.send_keys(LOGIN_ACCOUNT)
        secret_input = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[1]/div/div[1]/form/div[2]/div/input')))
        secret_input.clear()
        secret_input.send_keys(LOGIN_SECRET)
        login_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[2]/div[2]/div[2]')))
        login_btn.click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="lg_tbar"]/div/div[2]/ul/li[5]/span')))

    def create_search_url(self):
        url = SEARCH_URL + KEY_WORD + '/'
        url = url + 'p-city_213' # 广州
        url = url + '-gm_4_5_6' # 规模：150-500人、500人-2000人、2000人以上
        url = url + '-jd_5_6_7' # 阶段：C轮、D轮、上市公司
        url = url + '?'
        url = url + 'px=new' # 最新排序
        url = url + '&gj=3年及以下,3-5年' #工作经验：3年以下，3年到5年
        url = url + '&xl=本科' # 学历：本科
        url = url + '#filterBox'
        return url

    def crawl(self, url):
        self.browser.get(url)

        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#order > li > div.item.page > div.page-number > span.span.totalNum')))
        doc = pq(self.browser.page_source)
        total_page = doc('#order > li > div.item.page > div.page-number > span.span.totalNum').text()
        self.index_page()
        for current_page in range(1, int(total_page), 1):
            next_page = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#s_position_list > div.item_con_pager > div > span.pager_next')))
            next_page.click()
            self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#s_position_list > div.item_con_pager > div > span.pager_is_current'), str(current_page + 1)))
            sleep(1)
            self.index_page()

    def index_page(self):
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        '#s_position_list > ul > li.con_list_item.first_row.default_list > div.list_item_top > div.position > div.p_top > a > h3')))
        doc = pq(self.browser.page_source)
        items = doc('#s_position_list > ul > li').items()
        for item in items:
            salary = item.find('div.list_item_top > div.position > div.p_bot > div > span').text()
            item.find('div.list_item_top > div.position > div.p_bot > div > span').remove()
            info = {
                '时间' : item.find('div.list_item_top > div.position > div.p_top > span').text(),
                '岗位' : item.find('div.list_item_top > div.position > div.p_top > a > h3').text(),
                '薪资' : salary,
                '公司' : item.find('div.list_item_top > div.company > div.company_name > a').text(),
                '地点' : item.find('div.list_item_top > div.position > div.p_top > a > span > em').text(),
                '经验' : item.find('div.list_item_top > div.position > div.p_bot > div').text(),
                '介绍' : item.find('div.list_item_top > div.company > div.industry').text(),
                '优势' : item.find('div.list_item_bot > div.li_b_r').text(),
                '标签' : item.find('div.list_item_bot > div.li_b_l > span').text(),
                '链接' : item.find('div.list_item_top > div.position > div.p_top > a').attr('href')
            }
            self.save_to_mongo(info)

    def save_to_mongo(self, result):
        try:
            if self.db[MONGO_COLLECTION].insert(result):
                print('mongodb insert success.')
        except Exception:
            print('mongodb insert fail.')

if __name__=='__main__':
    handler = Handler()
    handler.on_start()