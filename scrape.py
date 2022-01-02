from classes import *
from datetime import datetime as dt
from lxml import html
import json
import re
import requests

def clean(l):
    return [item.strip() for item in l if item.strip() != '']

def scrape_shelf(name: str, shelf_url: str) -> list[Book]:
    def page_url(page=1):
        return shelf_url + f'&page={page}'

    def attrib_path(attribute):
        base = "/html/body//table[@id='books']"
        return f"{base}//td[@class='field {attribute}']/div[@class='value']"

    def parse_titles(titles):
        def parse(title):
            t = title.text.strip()
            s = NULL, NULL
            if len(title.getchildren()) != 0:
                series = title.getchildren()[0].text.strip()
                s = re.split(',? #', series[1:-1]) 
                s[1] = float(s[1])
            return t, s[0], s[1]
        return list(zip(*[parse(title) for title in titles]))

    def parse_ratings(ratings):
        m = { 'did not like it': 1,
            'it was ok': 2, 
            'liked it': 3,
            'really liked it': 4,
            'it was amazing': 5,
            NULL: 0 }
        return [m[r.getchildren()[0].get('title', NULL)] for r in ratings]

    books = []
    for i in range(1, 100): # pages
        req = requests.get(page_url(i))
        if 'No matching items!' in req.text:
            break
        tree = html.fromstring(req.text)

        titles, series, orders = parse_titles(tree.xpath(attrib_path('title') + '/a'))
        authors = tree.xpath(attrib_path('author') + '/a/text()')
        pages = clean(tree.xpath(attrib_path('num_pages') + '/nobr/text()'))
        pages = [int(pg.replace(',', '')) for pg in pages]
        date_read = clean(tree.xpath(attrib_path('date_read') + '//text()'))
        date_read = [dt.strptime(d, '%b %d, %Y').strftime('%Y-%m-%d') if d != 'not set' else NULL for d in date_read]
        ratings = parse_ratings(tree.xpath(attrib_path('rating')))
        
        b = list(zip(titles, series, orders, authors, pages, date_read, ratings))
        books.extend(b)

    return [Book(*b) for b in books]

def scrape_user(base_url: str):
    user = User()

    mainpage = requests.get(base_url)
    tree = html.fromstring(mainpage.text)
    path = "/html/body//div[@class='userShelf']/a/@href"
    shelf_names = [s[s.index('?shelf=')+7:] for s in tree.xpath(path)]

    for s in shelf_names:
        books = scrape_shelf(s, base_url + f'?shelf={s}')
        for b in books:
            user.add_book(b, s)
    return user

