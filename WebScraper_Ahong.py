'''
主題:
爬蟲小說網站 https://big5.quanben5.com/
使用語言:
Python 3.11.1 作者:侯坤宏 最後更新日:2023/1/28
模組:
requests 2.28.2
BeautifulSoup4 4.11.1
pandas 1.5.3
'''
import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}
def Website_Book_one_Chapter(one_url):  #拿到網站>>一系列>>一本書>>一章節 (故事內容)
    r = requests.get(url=one_url ,headers=headers)
    r.encoding ="utf-8"
    soup = BeautifulSoup(r.text, 'html.parser')
    tag_name = '.wrapper .content p'
    articles = soup.select(tag_name)
    data =[]
    for art in articles:
        art = art.text
        art = art.replace('()','').replace('上一頁','').replace('目錄','').replace('下一頁','').replace('&l','').replace('&g','')
        data.append(art)
    df = pd.DataFrame(data)
    df = df.dropna(axis=1)
    df.to_csv('full_station_novel.csv', mode='a', encoding='UTF-8',index=False)

def Website_one_Book(index_url):  #拿到網站>>一系列>>一本書 (章節網址)
    index_r = requests.get(url=index_url ,headers=headers)
    index_r.encoding ="utf-8"
    soup = BeautifulSoup(index_r.text, 'html.parser')
    index_tag_name = 'ul.list li a'
    index_articles = soup.select(index_tag_name)
    for index_art in index_articles:
        index_art_url = ('https://big5.quanben5.com/'+index_art['href'])
        Website_Book_one_Chapter(index_art_url)

def Website_series(series_url): #拿到網站>>一系列 (拿到一系列全部網址)
    series_First_url = 'https://big5.quanben5.com/category/1.html'
    series_First_r = requests.get(url=series_First_url ,headers=headers)
    series_First_r.encoding ="utf-8"
    series_First_soup = BeautifulSoup(series_First_r.text, 'html.parser')
    Page_name = '.nlist_page p.grey span'
    series_Page = series_First_soup.select(Page_name)
    for series_Page_1 in series_Page:
        series_Page_1 = series_Page_1.text
        series_Page_1 = series_Page_1.replace('1 / ','') #總頁數
    series_Page_1 = int(series_Page_1)
    for i in range(series_Page_1):
        if i == 0:
            series_url ='https://big5.quanben5.com/category/'+'1.html'
        elif i != 0:
            series_url ='https://big5.quanben5.com/category/'+'1_{}.html'.format(i+1)
        series_r = requests.get(url=series_url ,headers=headers)
        series_r.encoding ="utf-8"
        series_soup = BeautifulSoup(series_r.text, 'html.parser')
        tag_name = '.pic_txt_list h3 a '
        series_articles = series_soup.select(tag_name)
        for series_art in series_articles:
            series_art = ('https://big5.quanben5.com/'+series_art['href']+'xiaoshuo.html')
            Website_one_Book(series_art)

def Website(front_page_url):
    front_page_r = requests.get(url=front_page_url ,headers=headers)
    front_page_r.encoding ="utf-8"
    front_page_soup = BeautifulSoup(front_page_r.text, 'html.parser')
    tag_name = '.nav a'
    front_page_articles = front_page_soup.select(tag_name)
    for front_page_art in front_page_articles:
        front_page_art = (front_page_art['href'])
        front_page_art = 'https://big5.quanben5.com/'+front_page_art
        Website_series(front_page_art)

Website('https://big5.quanben5.com/')
