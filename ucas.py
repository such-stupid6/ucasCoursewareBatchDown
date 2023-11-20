import requests_html
from bs4 import BeautifulSoup
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class UCAS:
    def __init__(self):
        # self.jsessionid = ''
        self.session = requests_html.HTMLSession()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
        }
        self.ClassSite = ''
        self.course_dic = []
        self.titleIndex = ["PDF","文本","图片","PowerPoint ","Excel","Mpeg4视频","未知类型"]
        dirIndex="文件夹"
    
    def login(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        # capabilities = DesiredCapabilities.CHROME.copy()
        # capabilities['acceptSslCerts'] = True
        browser = webdriver.Chrome(options=options)
        browser.get('https://sep.ucas.ac.cn')
        # browser.set_window_size(1920, 1080)
        # browser.find_element_by_id('userName1').send_keys(self.username)
        # browser.find_element_by_id('pwd').send_keys(self.password)
        WebDriverWait(browser, 600).until(EC.presence_of_element_located((By.ID, 'popbox1')))
        # self.jsessionid = browser.get_cookie('JSESSIONID')['value']
        self.session.cookies.update({cookie['name']: cookie['value'] for cookie in browser.get_cookies()})
        return 

    def getClassSite(self):
        url = 'https://sep.ucas.ac.cn/appStore'
        html = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(html.text, 'html.parser')
        portal_url = 'http://sep.ucas.ac.cn' + soup.find_all(name='a', attrs={'title': '课程网站'})[0]['href']
        # print(portal_url)
        self.ClassSite = portal_url

    def getCourseInfo(self):
        print("visiting ", self.ClassSite)
        html = self.session.get(url=self.ClassSite, headers=self.headers)
        # print(html.status_code)
        time.sleep(3)
        # print(html.text)
        soup = BeautifulSoup(html.text, 'html.parser')
        # print(soup.find_all(name='h4')[1].a['href'])
        trueUrl = soup.find_all(name='h4')[1].a['href']
        print("visiting ",trueUrl)
        html = self.session.get(url=trueUrl, headers=self.headers)
        html.html.render()
        # with open('output.html', 'w', encoding='utf-8') as file:
        #     file.write(html.text)
        # print(html.text)
        soup = BeautifulSoup(html.text, 'html.parser')
        # print(soup.find_all(name='a', attrs={'title': '我的课程 - 查看或加入站点'}))
        courseUrl = soup.find_all(name='a', attrs={'title': '我的课程 - 查看或加入站点'})[0]['href']
        print("visiting ",courseUrl)
        course_html = self.session.get(url=courseUrl, headers=self.headers)
        course_html.html.render()
        course_soup = BeautifulSoup(course_html.text, 'html.parser')
        course_list = course_soup.find_all(name='tr')
        print(course_list)
        course_tmp = []
        for course in course_list:
            if len(course.find_all(name='a', attrs={'target': '_top'})) > 0:
                course_tmp.append(course.find_all(name='a')[0].text) # 课程名称
                course_tmp.append(course.find_all(name='a')[0]['href']) # 小课程url
                self.course_dic.append(course_tmp)
                course_tmp=[]
            else:
                pass
        print("here is your course list:")
        for i,co in enumerate(self.course_dic):
            print(i,co[0])
        target = input("输入你想下载的课程，以空格分界: ").split()
        for i in target:
            url = self.course_dic[int(i)][1]
            
            print("visiting ",url)
            html = self.session.get(url=url, headers=self.headers)
            html.html.render()
            soup = BeautifulSoup(html.text, 'html.parser')
            # print(soup.find_all(name='a', attrs={'title': '资源 - 上传、下载课件，发布文档，网址等信息'}))
            sourceUrl = soup.find_all(name='a', attrs={'title': '资源 - 上传、下载课件，发布文档，网址等信息'})[0]['href']
            print("visiting ",sourceUrl)
            self.getIter(sourceUrl)
        

    def getIter(self, url):
        # print(target) 
            source_html = self.session.get(url=url, headers=self.headers)
            source_html.html.render()
            source_soup = BeautifulSoup(source_html.text, 'html.parser')
            source_list = source_soup.find_all(name='tr')
            # print(source_list)
            source_tmp = []
            result = []
            for source in source_list:
                for title in self.titleIndex:
                    if len(source.find_all(name='a', attrs={'title': title, 'target': '_blank'})) > 0:
                        for item in source.find_all(name='a', attrs={'title': title, 'target': '_blank'}):
                            source_tmp.append(item['href'])
                            result.append(source_tmp)
                            source_tmp=[]
                if len(source.find_all(name='a', attrs={'title': "文件夹"})) > 0:
                    for element in source.find_all(name='a', attrs={'title': "文件夹"}):
                        # print("find dir: ",element)
                        js = element.get('onclick')
                        print(js)
                            



                            
            print(result)

            
            
        # url = self.course_dic[target][1]
        # print("visiting ",url)
        # html = self.session.get(url=url, headers=self.headers)
        # for item in self.course_dic:
        #     print(item[0])

    def run(self):
        self.login()
        self.getClassSite()
        self.getCourseInfo()


if __name__ == '__main__':
    ucas = UCAS()
    ucas.run()