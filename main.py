# -*- coding:utf-8 -*-
import re
import pymysql
import requests
# 这里改成config
from config import config
from bs4 import BeautifulSoup as bs

s = requests.Session()


def is_last_page(htmlFrom):
    soup = bs(htmlFrom, 'html.parser')
    last = soup.find('span', 'next')
    if not last:
        return False
    next = last.find('a')
    if next:
        return False
    else:
        return True


def from_html_list(htmlFrom):
    soup = bs(htmlFrom, 'html.parser')
    movies = []
    for item in soup.find_all("div", "item"):
        movie = {}
        movie['url'] = item.find("a", "nbg")['href']
        movie['title'] = item.find("em").text
        # movie['intro'] = item.find("li", "intro").text
        rateLine = item.find("span", "date").parent
        movie['my_date'] = item.find("span", "date").text
        tags = item.find("span", "tags")
        if tags and tags.text:
            movie['my_tags'] = tags.text
        else:
            movie['my_tags'] = ''
        starObj = re.search(r'\d+', rateLine.find("span")['class'][0])
        if starObj:
            star = starObj.group()
        else:
            star = 0
        movie['my_rate'] = star
        comment = item.find("span", 'comment')
        if comment:
            movie['my_comment'] = comment.text
        else:
            movie['my_comment'] = ''
        movies.append(movie)
    return movies


def get_cursor():
    db = get_db()
    return db.cursor()


def update_lists():
    db = get_db()
    c = db.cursor()

    # id>=1000
    sql = """
          select * from favorite_movie
          where 1
            and rate is null 
          order by id asc
         """
    c.execute(sql)
    res = c.fetchall()
    for item in res:
        spider_item(item[1], item[0], item[3])


def spider_item(url, id, title):
    id = int(id)
    headers = {'user-agent': 'Mozilla/5.0'}
    r = s.get(url, headers=headers)
    html = r.text
    soup = bs(html, 'html.parser')
    titleDom = soup.find("title")
    if titleDom and titleDom.text and '页面不存在' == titleDom.text.strip():
        print(title, '页面不存在')
        return

    h1Dom = soup.find("h1")
    if h1Dom:
        year = h1Dom.find("span", "year").text
    else:
        # 认为没有标题 有问题
        # 检测到有异常请求从你的 IP 发出，请 登录 使用豆瓣。
        # todo ip 池方案
        print('error page')
        print(soup)
        return

    yearRegObj = re.search(r'\d+', year)
    if yearRegObj:
        year = yearRegObj.group()

    info = soup.find("div", id="info").text.strip()
    rateDom = soup.find("strong", "ll rating_num")
    if rateDom:
        rate = rateDom.text
    else:
        rate = 0

    ratingLine = soup.find('a', "rating_people")
    if ratingLine:
        saw_times = ratingLine.find("span").text
    else:
        saw_times = 0

    sql = "update favorite_movie set rate=%s,year=%s,saw_times=%s,info=%s where id=%s;"
    values = (rate, year, saw_times, info, int(id))

    db = get_db()
    c = db.cursor()

    try:
        c.execute(sql, values)
        db.commit()
    except Exception as error:
        db.rollback()
        print(sql)
        print(error)
        exit('更新失败')

    print('id %d title %s done!' % (id, title))


def spider_list(page=0):
    print("开始爬第%d页" % page)

    # todo 这里后期是动态的
    url = 'https://movie.douban.com/people/' \
          + config['douban']['alias'] \
          + '/collect?start=' \
          + str(page * 15) \
          + '&sort=time&rating=all&filter=all&mode=grid'
    headers = {'user-agent': 'Mozilla/5.0'}

    print(url)
    try:
        r = s.get(url, headers=headers)
        r.raise_for_status()
        return r.text
    except Exception as error:
        print('第%d页爬失败了' % page)
        print(error)
    return ''


# todo 如果有验证码，让用户输入
def login_quite():
    login_url = 'https://accounts.douban.com/j/mobile/login/basic'
    headers = {'user-agent': 'Mozilla/5.0', 'Referer': 'https://accounts.douban.com/passport/login?source=main'}

    data = {
        "name": config['douban']['name'],
        "password": config['douban']['password'],
        'remember': 'false',
    }
    try:
        r = s.post(login_url, headers=headers, data=data)
        print('登录成功')
        r.raise_for_status()
    except:
        print('登录请求失败')
        return 0
    # 打印请求结果
    print(r.text)
    return 1


def get_db():
    c = config['database']
    return pymysql.Connect(c['host'], c['user'], c['password'], c['database'])


def store(lists):
    db = get_db()
    c = db.cursor()

    cols = """
    url
    ,title
    ,my_rate
    ,my_date
    ,my_tags
    ,my_comment
    """
    sql = "insert into favorite_movie(" + cols + ")" + " values (%s,%s,%s,%s,%s,%s)"
    insert = []
    for item in lists:
        print(item['my_tags'])

        insert.append((
            item['url']
            , item['title']
            , item['my_rate']
            , item['my_date']
            , item['my_tags']
            , item['my_comment']
        ))

    try:
        res = c.executemany(sql, insert)
        db.commit()
    except Exception as err:
        db.rollback()
        print(err)
        exit('fuck mysql')
    print("共更新%s条" % res)
    # 关闭数据库连接
    db.close()
    return True


def get_item_detail(url):
    headers = {'user-agent': 'Mozilla/5.0'}
    print(url)
    try:
        r = s.get(url, headers=headers)
        r.raise_for_status()
        return r.text
    except Exception as error:
        print('该条目失败%s' % url)
        print(error)
    return ''


if __name__ == '__main__':
    # 如果需要登录
    # login_quite()

    page = 0
    isLast = False

    while (page < 1000) and (not isLast):
        html = spider_list(page)
        print('main page %d' % page)
        if not html:
            break
        lists = from_html_list(html)
        res = store(lists)
        isLast = is_last_page(html)
        page += 1
        print(isLast, page)
        # print(lists)
        print(res)

    # 遍历详情页，然后更新其他信息
    update_lists()
