from classes import *
from notion import *
from scrape import *

helen = scrape_user('https://www.goodreads.com/review/list/114627424-helen')

with open('key.json', 'r') as file:
    file = json.load(file)
    NOTION_TOKEN = file['NOTION_TOKEN']
    parent_id = file['parent_id']

BookDB(NOTION_TOKEN, 'books', parent_id, helen)

