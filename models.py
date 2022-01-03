from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Book(Base):
    __tablename__ = 'Books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    author = Column(String(50))
    pages = relationship("Page", backref='book')

    def __repr__(self):
        return "<Book('%d', '%s','%s')>" % (self.id, self.name, self.author)


class Page(Base):
    __tablename__ = 'Pages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer)
    book_id = Column(Integer, ForeignKey('Books.id'))
    data = Column(LargeBinary(2**20))

    def __repr__(self):
        return "<Page('%s','%s', 'len(%d)')>" % (self.number, self.book_id, len(self.data))
