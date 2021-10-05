
# -*- coding: utf-8 -*-
# -----------------------------------------------------------
# Parse sitemap 'https://meduza.io/'
#
# (C) 2021 Cherenkov Denis, Chelyabinsk, Russia
# -----------------------------------------------------------
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import db_for_url as db
import json
import datetime
import pylab as plt

#sample data in the site map
patt = """
<url>
   <loc>{0}</loc>
   <lastmod>{1}</lastmod>
   <changefreq>weekly</changefreq>
   <priority>0.5</priority>
</url>
"""

url_from_page_start = []
urls_met = []
stack = []
url = 'https://meduza.io/'
host = 'https://meduza.io/'

def get_page(html: str) -> str:
    '''Get a page
     param html [URL address of the page for parsing]
     '''
    page = requests.get(html)
    return page


def get_title(html: str) -> str:
    '''Get the page title
    param html [URL address of the page for parsing]
    '''
    page = requests.get(html)
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, 'html.parser')
        title=soup.title.text 
        return title
    else:
        raise Exception ('Error. Title was not parsed.')
      


def get_content(html: str) -> str:
    '''Get urls from the page and verifies their correct
    param html [URL address of the page for parsing]
    '''
    url = []
    page = get_page(html)
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, 'html.parser')
        for a in (tag['href'] for tag in soup('a')):
            if not a.startswith('http'):
                a = urljoin(host, a)
            url.append(a)
        return url
    else:
        raise Exception ('Error. Url was not parsed.')


def check_in_or_out_url(html: str) -> str:
    '''Checking external and internal links
    param html [URL address of the page for parsing]
    '''
    print('check ' + html)
    if html.startswith(host):
        print("in url - " + html)
        return html
    else:
        print("out url - " + html)
        raise Exception ('Error. Url is out.')


url_from_page_start = get_content(url)
now = datetime.datetime.now()
out=open('sitemap.xml', 'w')
print(len(url_from_page_start))
db.create_db()
db.create_db_follow()
for i in url_from_page_start:
    if i not in stack:
        title = get_title(i)
        db.add_db(i, title)
        out.write(patt.format(i, now) + '\n')
        urls_met.append(i)
        stack.append(i)
        db.add_db_follow(url, i)
    else:
        db.add_count_in_db(i)
print('stack - ' + str(len(stack)))
while stack != []:
    print('len stack = ' + str(len(stack)))
    url_from_stack = stack.pop()
    while check_in_or_out_url(url_from_stack) == 'Error. Url is out.':
        db.add_count_in_db(url_from_stack)
        url_from_stack = stack.pop()
    else:
        new_urls = get_content(url_from_stack)
        if url_from_stack in urls_met:
            print('new_urls - ' + str(len(new_urls)))
        for i in new_urls:
                if i not in urls_met:
                    title = get_title(i)
                    db.add_db(i, title)
                    out.write(patt.format(i, now) + '\n')
                    stack.append(i)
                    urls_met.append(i)
                    db.add_db_follow(url_from_stack, i)
                else:
                    db.add_count_in_db(i)
                    db.add_db_follow(url_from_stack, i)
else:
    print('end')
    out.close()
