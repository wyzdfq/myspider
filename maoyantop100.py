import requests
import re
from urllib.parse import urlencode
from multiprocessing import Pool
import json
from requests.exceptions import RequestException



headers = {
    'Referer': 'http://maoyan.com/board/4',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
}

def get_page(offset):
    data = {'offset':offset}
    try:
        res = requests.get('http://maoyan.com/board/4?'+urlencode(data),headers=headers)
        if res.status_code == 200:
            #print(res.text)
            return res.text
        return None
    except RequestException:
        print('请求页面出错')
        return None

def parse_page(html):
    pattern = re.compile('<dd>.*?>(\d+)</i>.*?<img data-src="(.*?)"\salt="(.*?)".*?"star">(.*?)</p>.*?"releasetime">(.*?)</p>.*?'
                         +'integer">(.*?)</i>.*?action">(.*?)</i>',re.S)
    items = re.findall(pattern,html)
    for item in items:
        yield {
            'index':item[0],
            'imgurl':item[1],
            'title':item[2],
            'actor':item[3].strip()[3:],
            'time':item[4][5:],
            'score':item[5]+item[6]
        }
def save(item):
    with open('result.txt','a',encoding='UTF-8') as f:
        f.write(json.dumps(item,ensure_ascii=False)+'\n')

def main(offset):
    html = get_page(offset)
    for item in parse_page(html):
        save(item)
        print('正在保存',item)

if __name__=='__main__':
    pool = Pool()
    pool.map(main, [str(i * 10) for i in range(10)])

