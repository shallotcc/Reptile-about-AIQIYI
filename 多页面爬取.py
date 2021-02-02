import requests
import re
import json
from urllib.parse import urlencode
from requests.exceptions import RequestException
import  爬虫学习.爬取爱奇艺电影用户评论及其关系.user as User
import time
import 爬虫学习.爬取爱奇艺电影用户评论及其关系.main as mn
from lxml import etree
import requests

def get_one_page(referer,num):
    params={
        'access_play_control_platform':'14',
        'channel_id': '1',
        'data_type': '1',
        'from': 'pcw_list',
        'is_album_finished': '',
        'is_purchase': '',
        'key': '',
        'market_release_date_level': '',
        'mode': '11',
        'pageNum': num,
        'pageSize': '48',
        'site': 'iqiyi',
        'source_type': '',
        'three_category_id': '',
        'without_qipu': '1',
    }
    headers={
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        "authority": "pcw-api.iqiyi.com",
        "method": "GET",

        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate,br",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type":"application/x-www-form-urlencoded",
        "origin":"https://list.iqiyi.com",
        "referer": referer
    }
    #params['path'] = '/search/video/videolists?access_play_control_platform=14&channel_id=1&data_type=1&from=pcw_list&is_album_finished=&is_purchase=&key=&market_release_date_level=&mode=11&pageNum=19&pageSize=48&site=iqiyi&source_type=&three_category_id=&without_qipu=1'
    url='https://pcw-api.iqiyi.com/search/video/videolists?'+urlencode(params)
    try:
        requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
        session = requests.session()
        session.keep_alive = False
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            # print(response.json())
            return response.json()
    except requests.ConnectionError as e:
        print("连接错误")
        print(e)
        print(e.args)
        return None

def parse_one_page(json,f1,f2,f3,f4,f5):
    if json==None:
        print("json为空")
        return None

    if json.get('data')!=['']:
        list=json.get('data').get('list')
        for movie in list:
            movie_name=movie.get('name')
            actors=movie.get('secondInfo')
            f1.writelines(movie_name+'\t'+actors+'\n')
            categories=movie.get('categories')#类型
            types=''#类型
            for category in categories:
                types+=category['name']+' '
            if movie.get('description'):
                description=movie.get('description')
            else:
                description='无'
            f4.writelines(movie_name+'\t类型：'+types+'\t简介：'+description+'\n')
            href=movie.get('playUrl')
            movie_id=movie.get('tvId')
            mn.main(href, movie_id,movie_name,f2,f3,f5)

if __name__ == '__main__':
    for i in range(1,20):
        url = 'https://list.iqiyi.com/www/1/-------------11-' + str(i) + '-1-iqiyi--.html'
        f1 = open('文件1-'+str(i)+'.txt','w',encoding='utf-8')    #主要演员
        f2 = open('文件2-'+str(i)+'.txt','w',encoding='utf-8')    #用户名 视频名称 评论 评分
        f3 = open('文件3-'+str(i)+'.txt','w',encoding='utf-8')    #用户名 视频名称 主评论 副评论
        f4 = open('文件4-'+str(i)+'.txt','w',encoding='utf-8')    #视频名称 标签（类型） 简介
        f5 = open('文件5-'+str(i)+'.txt','w',encoding='utf-8')    #视频名称 导演
        my_json=get_one_page(url,i)
        parse_one_page(my_json,f1,f2,f3,f4,f5)
        f1.close()
        f2.close()
        f3.close()
        f4.close()
        f5.close()
        #print(type(href))
        #print(type(movie_id))


