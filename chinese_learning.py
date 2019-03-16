import requests
import time
from bs4 import BeautifulSoup as bs


url_index = "http://59.69.102.9/zgyw/index.aspx"
url_study = "http://59.69.102.9/zgyw/study/LearningIndex.aspx"


def login():
    name = input("请输入学号：")
    pwd = input("请输入密码（默认不填即为学号）：")
    if not name:
        print("请输入学号！")
        sys.exit()
    if not pwd:
        pwd = name
    s = requests.Session()
    try:
        soup = bs(s.get(url_index, timeout=8).text, 'lxml')
        viewstate = soup.find('input', {"id": "__VIEWSTATE"})['value']
        data = {
            "ctl00$ContentPlaceHolder1$name": name,
            "ctl00$ContentPlaceHolder1$pwd": pwd,
            "ctl00$ContentPlaceHolder1$login": "登录",
            "__VIEWSTATE": viewstate
        }
        s.post(url_index, data=data)
        print("\n愉快的大学语文学习之旅开始啦！！！\n")
        while True:
            startLearning(s)
    except requests.exceptions.Timeout:
        print("连接超时，情检查是否处于校园网环境后重试。\n")
        login()


def startLearning(session):
    soup = bs(session.get(url_index).text, 'lxml')
    session.get(url_study)
    try:
        learning_time = soup.find(
            'span', {"id": "ctl00_ContentPlaceHolder1_lblonlineTime"}).get_text()
        user_name = soup.find(
            'span', {"id": "ctl00_ContentPlaceHolder1_lblrealname"}).get_text()
        print("当前学习用户："+user_name+"\n"+"已学习时间： "+learning_time)
        print("休眠五分钟，减轻服务器压力。"+"\n")
        time.sleep(300)
    except AttributeError:
        print("登录出错，请检查用户名密码是否输入正确！\n")
        login()


def main():
    welcome = '''
作者：慕风
用途：刷大学语文学习１０００小时学习时间
条件：必须搭配校园网或ＶＰＮ食用
原理: 博客更新后文档丢失，有需要再填坑
博客： https://blog.moofeng.cn/
    '''
    print(welcome)
    login()


if __name__ == "__main__":
    main()
