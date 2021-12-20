NULL = ''

class Book:
    def __init__(self, title, series, order, author, pages, date_read, rating):
        self.title = title[:title.index(':')] if ':' in title else title
        self.series = series
        self.order = order
        self.author = author
        self.pages = pages
        self.date_read = date_read
        self.rating = rating
        self.shelves = []

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return f'{self.title} ({self.author})'

    @property
    def id(self):
        return str(self)

class Shelf:
    def __init__(self, name):
        self.name = name
        self.books = []

    @property
    def num_books(self):
        return len(self.books)

    def __contains__(self, book: Book):
        return book.id in [b.id for b in self.books]

    def __str__(self):
        return f'{self.name}, {self.num_books} books'

def shelf(book: Book, shelf: Shelf):
    book.shelves.append(shelf)
    shelf.books.append(book)

class User:
    def __init__(self):
        self.shelves = {} # name : Shelf
        self.books = {} # id : Book
    
    def add_book(self, b: Book, shelf_name: str):
        if b.id in self.books:
            b = self.books[b.id]
        else:
            self.books[b.id] = b
        if shelf_name not in self.shelves:
            self.shelves[shelf_name] = Shelf(shelf_name)
        shelf(b, self.shelves[shelf_name])

    @property
    def num_books(self):
        return len(self.books)

    def __str__(self):
        out = [f'{len(self.shelves)} shelves, {self.num_books} books']
        for shelf in self.shelves.values():
            out.append(str(shelf))
        return '\n'.join(out)