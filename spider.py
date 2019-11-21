# coding=utf-8
"""
　　__title__ = ''
　　__file__ = ''
　　__author__ = 'tianmuchunxiao'
　　__mtime__ = '2019/8/2'
"""

import requests
import json
import smtplib

from pprint import pprint
from email.mime.text import MIMEText
from email.header import Header

from config import *

URL = 'http://quotes.money.163.com/hs/service/diyrank.php'

HEADERS = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh,en-US;q=0.9,en;q=0.8,zh-TW;q=0.7,zh-CN;q=0.6',
    'Connection': 'keep-alive',
    'Host': 'quotes.money.163.com',
    'Referer': 'http://quotes.money.163.com/old/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

PARAMS = {
    'host': 'http://quotes.money.163.com/hs/service/diyrank.php',
    'page': '0',
    'query': 'STYPE:EQA',
    'fields': 'NO,SYMBOL,NAME,PRICE,PERCENT,UPDOWN,FIVE_MINUTE,OPEN,YESTCLOSE,HIGH,LOW,VOLUME,TURNOVER,HS,LB,WB,ZF,PE,MCAP,TCAP,MFSUM,MFRATIO.MFRATIO2,MFRATIO.MFRATIO10,SNAME,CODE,ANNOUNMT,UVSNEWS',
    'sort': 'SYMBOL',
    'order': 'asc',
    'count': '10240',
    'type': 'query'
}

def get_all_stock_data_list(url=URL, headers=HEADERS, params=PARAMS):
    response = requests.get(url=url, params=params, headers=headers)
    total = json.loads(response.content.decode('gbk'))['total']
    PARAMS['count'] = total

    response = requests.get(url=URL, params=PARAMS, headers=HEADERS)
    data_list = json.loads(response.content.decode('gbk'))['list']
    return data_list

def extract_mystock_info(stocks_data_list, stocks_id=mystocks):
    my_stocks_info = {}
    for id in stocks_id:
        my_stocks_info[id] = {}
    for stock_info in stocks_data_list:
        if stock_info["SYMBOL"] in my_stocks_info:
            my_stocks_info[stock_info["SYMBOL"]] = stock_info
    return my_stocks_info

def need_warn(stocks_info, stocks_cost_info=mystocks):
    result = {}
    for k, v in stocks_cost_info.items():
        if stocks_info[k]["PRICE"] >= v * threshold_ratio:
            result[k] = stocks_info[k]
    if not result:
        return False, result
    else:
        return True, result

def create_context(name, p1, p2):
    return f'{name} 今日报价：{p1:6.3f}, 距离你脱套价格:{p2:6.3f} 日益逼近，逃过成功率：{p1/p2:4.2f}，千万注意！'

def post_email(stocks_info, sender=zh_email_address, receivers=[zh_email_address], mystocks=mystocks):
    stocks_name = []
    msg = []

    for _, stock in stocks_info.items():
        stocks_name.append(stock["NAME"])
        msg.append(create_context(stock["NAME"], stock["PRICE"], mystocks[_]))

    msg.append("望君多加努力")
    msg = '\n'.join(msg)
    stocks_name = '、'.join(stocks_name)
    subject = f'今天的股票{stocks_name}值得关注呢'
    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码

    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = Header(FROM, 'utf-8')  # 发送者
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP(host, port)
        smtpObj.login(zh_email_address, authorization_code)
    except smtplib.SMTPException as e:
        print(e)
    try:
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print(e)
        print(f'出现了未知错误，无法发送邮件')


def test_email():
    subject = '今天的股票值得关注呢'
    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    msg = 'hhhh'
    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = Header(FROM, 'utf-8')  # 发送者
    # message['To'] = Header("zhaoheng", 'utf-8')  # 接收者
    message['Subject'] = Header(subject, 'utf-8')
    print(message.as_string())
    try:
        smtpObj = smtplib.SMTP(host, port)
        smtpObj.login(zh_email_address, authorization_code)
    except smtplib.SMTPException as e:
        print(e)
    try:
        receivers = [zh_email_address]
        smtpObj.sendmail(zh_email_address, receivers, message.as_string())

        # smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")

    except smtplib.SMTPException as e:
        print(e)
        print(f'出现了未知错误，无法发送邮件')


def detection():
    total_stocks_info = get_all_stock_data_list()
    stocks_info = extract_mystock_info(total_stocks_info)
    need_warn_stocks_info = need_warn(stocks_info)
    if not need_warn_stocks_info[0]:
        print('距离边界很远，不需要担心')
        print(need_warn_stocks_info[1])
        return
    else:
        stocks_info = need_warn_stocks_info[1]
        post_email(stocks_info)

# for row in data_list:
#     pprint(row)
#     # print('CODE', '代码', row['CODE'])
#     # print('FIVE_MINUTE', '五分钟涨跌', row['FIVE_MINUTE'])
#     # print('HIGH', '最高价', row['HIGH'])
#     # print('LOW', '最低价', row['LOW'])
#     # print('NAME', '股票名称', row['NAME'])
#     # print('OPEN', '开盘价', row['OPEN'])
#     # print('PERCENT', '涨跌幅', row['PERCENT'])
#     # print('PRICE', '价格', row['PRICE'])
#     # print('SYMBOL', '股票代码', row['SYMBOL'])
#     # print('TURNOVER', '成交额', row['TURNOVER'])
#     # print('UPDOWN', '涨跌额', row['UPDOWN'])
#     # print('VOLUME', '成交量', row['VOLUME'])
#     # print('YESTCLOSE', '昨收', row['YESTCLOSE'])
#     # print('ZF', '振幅', row['ZF'])

if __name__ == "__main__":
    # t =  [('中材国际',6.000, 8.072),
    #       ('中国船舶',20.150, 29.054)]
    # for a in t:
    #     b,c,d = a
    #     print(create_context(b,c,d))
    detection()