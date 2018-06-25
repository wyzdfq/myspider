from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymongo

#搜索内容
kw = '美女'


setting = [
    '--load-images=false',
    '--disk-cache=true'
]
browser = webdriver.PhantomJS(service_args=setting)
browser.set_window_size(1400,900)
response = browser.get('https://www.taobao.com/')
wait = WebDriverWait(browser,10)
#数据库
cilent = pymongo.MongoClient('localhost')
db = cilent['taobao']


def search(keyword):
    print('搜索中：',keyword)
    try:
        #搜索框
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'#q'))
        )
        #提交按钮
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_TSearchForm > div.search-button > button')))
        input.send_keys(keyword)
        submit.click()
        #页数
        index = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total')))
        parse_page()
        return int(index.text[2:-2])
    except TimeoutException:
        search()
#获取数据
def parse_page():
    html = pq(browser.page_source)
    items = html.find('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            #这里用src获取图片路径，有部分会错，搞不懂-_-
            'imgurl':item.find('.pic .img').attr('data-src'),
            'title':item.find('.title').text().replace('\n',' '),
            'price':item.find('.price').text(),
            'sold':item.find('.deal-cnt').text(),
            'shop':item.find('.shop').text(),
            'location':item.find('.location').text()
        }
        save(product)

#存到数据库
def save(product):
    try:
        if db['product'].insert(product):
            print('保存成功',product['title'])
    except Exception:
        print('保存失败',product)

#翻页
def next_page(page_number):
    print('翻页中',page_number)
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.form > input'))
        )
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()
        input.send_keys(page_number)
        submit.click()
        #验证页数
        wait.until(EC.text_to_be_present_in_element_value((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.form > input'),str(int(page_number)+1)))
        parse_page()
    except Exception:
        next_page(page_number)


def main():
    try:
        index = search(kw)
        for i in range(2,index+1):
            next_page(i)
    except Exception:
        print('出现错误')
    finally:
        browser.close()


if __name__ == '__main__':
    main()