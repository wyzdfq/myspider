import requests
from requests.exceptions import RequestException
from pyquery import PyQuery as pq


str='http://tieba.baidu.com'
f = open('test.txt', 'a')
#请求页面
def get_index_page():
    try:
        res = requests.get('http://tieba.baidu.com/f/index/forumclass')
        if res.status_code == 200:
            print('请求成功')
            return res.text
        return None
    except RequestException:
        print('请求页面出错')
        return None

#获取标签
def parse_index_page(res):
    html = pq(res)
    #父标签
    class_title = html.find('.class-item').items()
    for t in class_title:
        class_items=t.find('a').items()
        for i in class_items:
            product={
                'class':t.find('.class-item-title').text(),
                'tag':i.text(),
                'url':str + i.attr('href')
            }
            child_html=get_page(product)
            parse_page(child_html,product)
    f.close()

#请求子页面
def get_page(pd):
    try:
        res = requests.get(pd['url'])
        if res.status_code == 200:
            print('请求%s页面成功'% pd['tag'])
            return res.text
        return None
    except RequestException:
        print('请求%s页面成功', pd['tag'])
        return None


#分析爬取子页面

def parse_page(res,pd):
    htm=pq(res)
    i1=htm.find('.ba_content').items()
    for item in i1:
        pdt={
            'name':item.find('.ba_name').text(),
            '成员数':item.find('.ba_m_num').text(),
            '评论数':item.find('.ba_p_num').text()
        }
        data=[pd['class'],pd['tag'],pdt['name'],pdt['成员数'],pdt['评论数']]
        save(data)
        print(data)

#保存数据
def save(data):
    count = 0
    for i in data:
        if count == 0:
            f.write('\n')
            f.write(i)
            f.write('，')
            count += 1
        else:
            f.write(i)
            f.write('，')
            count += 1





if __name__=='__main__':
    res=get_index_page()
    parse_index_page(res)
