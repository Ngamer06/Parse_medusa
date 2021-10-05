import sqlite3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import requests
from bs4 import BeautifulSoup


conn = sqlite3.connect('medusa.db')
cur = conn.cursor()

def create_table_all_posts():
    '''
    Создание таблицы для всех спарсенных новостей
    '''
    cur.execute("""CREATE TABLE IF NOT EXISTS medusa_posts(
   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
   title TEXT,
   url TEXT);
    """)
    conn.commit()

def create_table_one_post():
    '''
    Создание таблицы для отдельных спарсенных новостей
    '''
    cur.execute("""CREATE TABLE IF NOT EXISTS medusa_one_post(
   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
   text TEXT,
   img TEXT);
    """)
    conn.commit()

def parse_all_posts(url, number_pages):
    '''
    Парсинг новостей с заданных страниц
    '''
    driver = webdriver.Firefox()
    driver.get(url)
    create_table_all_posts()
    driver.find_element_by_class_name("Switcher-module_knob__3kEy5").click()
    while number_pages != 0:
        try:
            driver.find_element_by_class_name('GDPRPanel-dismiss').click()
        except: pass
        # driver1 = driver.find_element_by_class_name('Chronology-footer')
        driver.find_element_by_css_selector("button[class^='Button-module_root__RpsiW']").click()
        # find_elements_by_css_selector("p[class^='SimpleBlock-module']")
        articles = driver.find_elements_by_class_name('Chronology-item')
        for i in articles:
            # print(i)
            post = i.find_element_by_class_name('ChronologyItem-link')
            url = post.get_attribute('href')
            # print(url)
            title = post.find_element_by_tag_name('strong').text
            # print(title)
            cur.execute("INSERT INTO medusa_posts(title, url) VALUES(?, ?)", (title, url))
            conn.commit()
        number_pages -=1
    driver.close()

def parse_one_post():
    '''
    Парсинг из отдельной новости текста и ссылок на картинки
    '''
    create_table_one_post()
    cur.execute("SELECT * FROM medusa_posts;")
    url_for_parse = cur.fetchall()
    driver = webdriver.Firefox()
    for z in range(len(url_for_parse)):
        print(url_for_parse[z][2])
        driver.get(url_for_parse[z][2])
        main_article = driver.find_element_by_class_name("GeneralMaterial-article") 

        block_text = main_article.find_elements_by_css_selector("p[class^='SimpleBlock-module']")
        text_article = ''
        for i in block_text:
            text = i.text
            text_article += text

        page = requests.get(url_for_parse[z][2])
        soup = BeautifulSoup(page.text, "html.parser")
        img_classes = soup.find_all("figure", class_=lambda c: 'EmbedBlock-module_root' in c)
        img_sources = []
        for i in img_classes:
            try:
                img_sources.append(i.find("img")['src'])
            except: pass
        img_sources_str = ', '.join(img_sources)
        cur.execute("INSERT INTO medusa_one_post(text, img) VALUES(?, ?)", (text_article, img_sources_str))
        print('insert')
        conn.commit()
    driver.close()





url_sitemap = 'https://meduza.io/'
number_pages = 2
parse_all_posts(url_sitemap, number_pages)
parse_one_post()
