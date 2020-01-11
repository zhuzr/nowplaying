#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import os
import link
import datetime
import sys  
from type import getType
header = {
    "User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16"}

def dbImport(id, name, actors, directors, soure, releaseDate):
    conn = link.get_conn()
    cursor = conn.cursor()
    time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    #html_escaped = MySQLdb.escape_string(html_content.encode('gb2312'))
    sql = "insert into douban_nowplaying (id, name, actors, directors, score, date, releaseDate) values (\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
          % (id, name, actors, directors, soure, time, releaseDate)
    updateSql = "update douban_nowplaying set score = \"%s\",date = \"%s\" where id = \"%s\";" % (soure, time, id)
    try:
        cursor.execute(sql)
        conn.commit()
    except:
        info = sys.exc_info()
        errStr = str(info[1])
        print("err info :", errStr)
        if errStr.find("1062") > 0:
            try:
                cursor.execute(updateSql)
                conn.commit()
            except:
                info = sys.exc_info()
                print("update err", info[0], ":", info[1], updateSql)
                conn.rollback()
    finally:
        conn.close


def get_html(web_url):
    html = requests.get(url=web_url, headers=header).text#不加text返回的是response，加了返回的是字符串
    Soup = BeautifulSoup(html, "lxml")
    data = Soup.find('div', id='nowplaying').find('ul').find_all('li', class_="list-item")
    return data

def get_detail(sub_url):
    html = requests.get(url=sub_url, headers=header).text#不加text返回的是response，加了返回的是字符串
    Soup = BeautifulSoup(html, "lxml")
    actorInfo = ''
    try:
        actors = Soup.find('div', id='info').find('span', class_='actor').find('span', class_='attrs').find_all('a')
        for actor in actors:
            actorInfo = actor.get_text() + '|' + actorInfo
        actorInfo = actorInfo[:-1] 
        print("演员：%s" % actorInfo)
    except:
        print("搜素演员名单失败！");
    directorInfo = ''
    try:
        directors = Soup.find('div', id='info').find('span', class_='attrs').find_all('a')
        for director in directors:
            directorInfo = director.get_text() + '|' +  directorInfo
        directorInfo = directorInfo[:-1]
        print("导演：%s" % directorInfo) 
    except:
        print("搜素导演名单失败！")
    try:
        score = Soup.find('div', class_='rating_self clearfix').find('strong', class_='ll rating_num').get_text()
        print("评分：%s" % score)
    except:
        print("获取评分失败");

    dateInfo = ''
    details = Soup.find('div', id='info').findAll('span', {'property': 'v:initialReleaseDate'});
    for detail in details:
        dateInfo = detail.get_text() + '/' + dateInfo
    dateInfo = dateInfo[:-1]
    print("上映日期：%s" % dateInfo) 

    return actorInfo, directorInfo, score, dateInfo

def get_info(all_move):
    f = open("/home/zhuzr/py/douban/msg", "a")

    for info in all_move:
        sub_url = info.find('li', class_='poster').find('a').get('href')
        title = info.find('li', class_='stitle').find('a').get('title')
        id = info.get('id')
        print(id)
        print(sub_url)
        print(title)

        actorInfo, directorInfo, score, releaseDate = get_detail(sub_url)
        dbImport(id, title, actorInfo, directorInfo, score, releaseDate) 
    f.close()  # 记得关闭文件


if __name__ == "__main__":
    if os.path.exists("/home/zhuzr/py/douban") == False:  # 两个if来判断是否文件路径存在 新建文件夹 删除文件
        os.mkdir("/home/zhuzr/py/douban")
    if os.path.exists("/home/zhuzr/py/douban/msg") == True:
        os.remove("/home/zhuzr/py/douban/msg")
    
    web_url = "https://movie.douban.com/cinema/nowplaying/shenzhen/"
    all_move = get_html(web_url)  # 返回每一页的网页
    get_info(all_move)  # 匹配对应信息存入本地
