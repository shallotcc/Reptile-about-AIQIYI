import requests
import re
import json
import  爬虫学习.爬取爱奇艺电影用户评论及其关系.user as User
from urllib.parse import urlencode
from requests.exceptions import RequestException
import time
from lxml import etree
import requests



def get_one_page(url):
    try:
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36'
        }
        response=requests.get(url,headers=headers)
        if response.status_code==200:
            #print(response.text)
            return response.text
        else:
            print("get请求出错")
            return None
    except RequestException:
        print("Request请求出错")
        return None

def parse_one_page(html,movie_name,f5):
    html=etree.HTML(html)
    actors_name=html.xpath('//*[@id="block-F"]/div[1]/div[1]/ul/li/div/div[2]/h3/a[1]/text()')
    director=actors_name.pop()
    f5.writelines(movie_name+'\t导演：'+director+'\n')
    '''
agent_type: 118
agent_version: 9.11.5
authcookie: null
business_type: 17
content_id: 1983386200
hot_size: 10
last_id: 
page: 
page_size: 10
types: hot,time
callback: jsonp_1573653878567_15914

agent_type: 118
agent_version: 9.11.5
authcookie: null
business_type: 17
content_id: 1983386200
hot_size: 0
last_id: 223909526021
page: 
page_size: 20
types: time
callback: jsonp_1573653888747_45309

agent_type: 118
agent_version: 9.11.5
authcookie: null
business_type: 17
content_id: 1983386200
hot_size: 0
last_id: 223902174921
page: 
page_size: 20
types: time
callback: jsonp_1573654070028_64193
    '''
#获取单页的json代码
def get_comment_page(referer,last_id,movie_id):
    params={
        "types": "time",
        "business_type": "17",
        "agent_type": "118",
        "agent_version": "9.11.5",
        "authcookie": "null",
    }
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        "Accept": "*/*",
        "Referer": referer,
        "Host": "sns-comment.iqiyi.com",
        "Connection": "keep-alive",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6",
        "Accept-Encoding": "gzip, deflate,br"
    }
    if last_id != "":
        params["last_id"] = last_id
    params['content_id'] = movie_id
    url="https://sns-comment.iqiyi.com/v3/comment/get_comments.action?"+urlencode(params)
    print(url)
    try:
        requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
        session=requests.session()
        session.keep_alive = False
        #print(movie_id)
        response=session.get(url,headers=headers)
        if response.status_code==200:
            #print(response.json())
            return response.json()
    except requests.ConnectionError as e:
        print("连接错误")
        print(e)
        print(e.args)
        return None

#获取单页的用户数据及其评论
def parse_comment_page(url,json,movie_name,f2,f3):
    last_id = "-1"
    #print(json)
    if json==None:
        return last_id
    if json.get('data')!=['']:
        last_id='-1'
        comments=json.get('data').get('comments')
        #print(type(json.get('data')))
        #print(type(comments))
        for comment in comments:
            last_id=comment.get('id')
            user_info=comment.get('userInfo')
            #评论信息
            if comment.get('content'):
                content=comment.get('content')
            else:
                content=' '
            #得到用户id和名字
            uid=user_info.get('uid')
            uname=user_info.get('uname')
            f2.writelines(uname+'\t'+movie_name+'\t'+content+'\n')
            f3.writelines(uname+'\t'+movie_name+'\t'+content+'\nreplies:\n')
            #得到评论字典 key=id,value=名字
            if comment.get('replies'):
                '''
                replies=comment.get('replies')
                for reply in replies:
                    if reply.get('content'):
                        reply_content=reply.get('content')
                    else:
                        reply_content=' '
                    reply_info=reply.get('userInfo')
                    reply_name=reply_info.get('uname')
                    reply_source=reply.get('replySource')
                    source_user=reply_source.get('userInfo')
                    source_user_name=source_user.get('uname')
                    f3.writelines('\t'+reply_name+'\t'+source_user_name+'\t'+reply_content+'\n')
             '''
                second_last_id=''
                while second_last_id != '-1':
                    item_json = get_second_comment_page(url, last_id, second_last_id)
                    second_last_id = parse_second_comment_page(item_json,f3)
                    time.sleep(0.2)


        return last_id
    else :
        return last_id


#获取单页二级评论的json代码
def get_second_comment_page(referer,content_id,last_id):
    params={
        "agent_type": "118",
        "agent_version": "9.0",
        "business_type": "17",
        "page_size":"10"
    }
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        "Accept": "*/*",
        "Referer": referer,
        "Host": "sns-comment.iqiyi.com",
        "Connection": "keep-alive",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate,br"
    }
    if last_id != "":
        params["last_id"] = last_id
    params['content_id'] = content_id
    #params['last_score'] = last_score
    url="https://sns-comment.iqiyi.com/v3/comment/get_second_comments.action?"+urlencode(params)
    try:
        requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
        session=requests.session()
        session.keep_alive = False
        #print(movie_id)
        response=session.get(url,headers=headers)
        if response.status_code==200:
            #print(response.json())
            return response.json()
    except requests.ConnectionError as e:
        print("连接错误")
        print(e)
        print(e.args)
        return None

#获取单页的二级评论用户数据及其评论
def parse_second_comment_page(json,f3):
    last_id = "-1"
    #print(json)
    if json==None:
        return last_id
    if json.get('data')!=['']:
        last_id='-1'
        comments=json.get('data').get('comments')
        #print(type(json.get('data')))
        #print(type(comments))
        for comment in comments:
            last_id=comment.get('id')
            user_info=comment.get('userInfo')
            #评论信息
            if comment.get('content'):
                content=comment.get('content')
            else:
                content=' '
            #得到用户id和名字
            uid=user_info.get('uid')
            uname=user_info.get('uname')
            if comment.get('replySource'):
                reply_source = comment.get('replySource')
                source_user = reply_source.get('userInfo')
                source_user_name = source_user.get('uname')
                f3.writelines('\t' + uname + '\t' + source_user_name + '\t' + content + '\n')
        return last_id
    else :
        return last_id






def main(url,movie_id,movie_name,f2,f3,f5):
    #users=[]
    html=get_one_page(url)
    parse_one_page(html,movie_name,f5)
    last_id=''
    while last_id !='-1':
        item_json=get_comment_page(url,last_id,movie_id)
        last_id=parse_comment_page(url,item_json,movie_name,f2,f3)
        time.sleep(0.5)
    f2.writelines('\n\n')
    f3.writelines('\n\n')
    print("页面已经爬取完成")
    '''
    for user in users:
        f3.writelines(user.uname+'\t'+movie_name+'\t'+)
        f3.writelines('\n')
        f3.writelines('replies:')
        for reply in user.replies.keys():
            f3.writelines(reply+'    ')
        f3.writelines('\n')
    '''


