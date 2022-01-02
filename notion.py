from classes import *
from notion_client import Client
from notion_client.helpers import get_id

class BookDB:
    def __init__(self, token, db_name, parent_id, user: User):
        self.client = Client(auth=token)
        title = [{'type': 'text', 'text': {'content': db_name}}]
        icon = {'type': 'emoji', 'emoji': '📚'}
        parent = {'type': 'page_id', 'page_id': parent_id}

        properties = {
            'Title': {'title': {}},  
            'Author': {'rich_text': {}},
            'Series': {'rich_text': {}},
            'Order': {'number': {'format': 'number'}},
            'Status': {
                'select': {
                    'options': [
                        {'name': 'Reading', 'color': 'yellow'},
                        {'name': 'Finished', 'color': 'gray'},
                        {'name': 'Want to read', 'color': 'blue'},
                    ]
                }
            },
            'Pages': {'number': {'format': 'number'}},
            'Date read': {'date': {}},
            'Shelves': {
                'type': 'multi_select',
                'multi_select': {
                    'options': [],
                },
            },
            'Rating': {'number': {'format': 'number'}},
        }

        self.db = self.client.databases.create(
            parent=parent, title=title, properties=properties, icon=icon)

        self.add_shelves(user.shelves.keys())
        for book in user.books.values():
            self.add_book(book)

    def add_shelves(self, shelves):
        db_id = self.db['id']
        options = [{'name': s, 'color': 'default'} for s in shelves]
        self.client.databases.update(
            database_id = db_id,
            properties = {
                'Shelves': {
                    'type': 'multi_select',
                    'multi_select': {
                        'options': options,
                    },
                },
            })

    def add_book(self, book: Book):
        db_id = self.db['id']
        parent = {'database_id': db_id}

        shelves = [{'name': shelf.name} for shelf in book.shelves]
        finished = book.date_read != NULL

        properties = {
            'Title': {
                'type': 'title',
                'title': [{ 'type': 'text', 
                            'text': { 'content': book.title } }]
            },
            'Author': {
                'type': 'rich_text',
                'rich_text': [{ 'type': 'text', 
                                'text': { 'content': book.author } }]
            },
            'Status': {
                'type': 'select',
                'select': { 'name': 'Finished' if finished else 'Want to read' }
            },
            'Pages': {
                'type': 'number',
                'number': book.pages
            },
            'Shelves': {
                'type': 'multi_select',
                'multi_select': shelves,
            },
        }

        # series
        if book.series != NULL:
            properties['Series'] = { 'type': 'rich_text',
                'rich_text': [{ 'type': 'text', 'text': { 'content': book.series } }] }
            properties['Order'] = { 'type': 'number', 'number': book.order }

        # read
        if finished:
            properties['Date read'] = { 'type': 'date', 'date': { 'start': book.date_read } }
            properties['Rating'] = { 'type': 'number', 'number': book.rating }

        self.client.pages.create(parent=parent, properties=properties)