'''
主題:
爬蟲小說網站 https://big5.quanben5.com/
使用語言:
Python 3.11.1 64-bit 作者:侯坤宏 最後更新日:2024/01/05
模組:
requests 2.28.2
BeautifulSoup4 4.11.1
pandas 1.5.3
PyMySQL 1.1.0
SQLAlchemy 2.0.25
'''
import requests
from bs4 import BeautifulSoup
import pandas as pd
import pymysql 
from sqlalchemy import create_engine

# MySQL 連線參數
booktitle_db = pymysql.connect(
    user = 'root',
    host = '127.0.0.1' ,
    port = 3306 ,
    charset = 'utf8',
    db = 'booktitle'
)
 
engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/booktitle', echo=False)

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}

def parse_chapter_name(chapter_name):#章節書名分開
    parts = chapter_name.split(' ')
    chapter = parts[0]
    name = ' '.join(parts[1:])
    return chapter, name 


def Website_one_Book(index_url):#拿到網站>>一系列>>書名
    index_r = requests.get(url=index_url, headers=headers)
    index_r.encoding = "utf-8"
    soup = BeautifulSoup(index_r.text, 'html.parser')
    index_tag_name = 'ul.list li a'
    index_articles = soup.select(index_tag_name)
    data = []
    for idx, index_art in enumerate(index_articles):
        index_art_text = index_art.text
        chapter, name = parse_chapter_name(index_art_text)
        data.append({'chapter': chapter, 'name': name})

    df = pd.DataFrame(data)
    #加入 id 欄位
    df['id'] = range(1,len(df)+1)  
    # 排序
    df = df[['id', 'chapter', 'name']]
    # 將資料寫入 MySQL 
    df.to_sql(name='booktitle', con=engine, if_exists='append', index=False)
    
    
 
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
 
#關閉數據讀取
booktitle_db.close()
print('資料已全部匯入')
