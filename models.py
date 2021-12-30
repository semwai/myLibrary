from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, LargeBinary
from sqlalchemy.orm import mapper
from sqlalchemy import MetaData

metadata = MetaData()

class Book(object):
    def __init__(self, name, author):
        self.name = name
        self.author = author

    def __repr__(self):
        return "<Book('%s','%s')>" % (self.name, self.author)


Books_table = Table('Books', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    Column('author', String(50))
)

mapper(Book, Books_table) 


class Page(object):
    def __init__(self, number, book_id, data):
        self.number = number
        self.book_id = book_id
        self.data = data

    def __repr__(self):
        return "<Page('%s','%s', 'len(%d)')>" % (self.number, self.book_id, len(self.data))


pages_table = Table('Pages', metadata,
    Column('id', Integer, primary_key=True),
    Column('number', Integer),
    Column('data', LargeBinary(length=10_000_000)),
    Column('book_id', ForeignKey('Books.id'))
)

mapper(Page, pages_table) 
