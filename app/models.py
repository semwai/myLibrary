from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), nullable=False)
    password = Column(String(256), nullable=False)
    books = relationship("Book", cascade="all,delete", backref='user')
    progress = relationship("UserProgress", cascade="all,delete")

    def __repr__(self):
        return "<User('%d', '%s','%s')>" % (self.id, self.name, self.email)


class Book(Base):
    __tablename__ = 'Books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    author = Column(String(50))
    pages = relationship("Page", cascade="all,delete", backref='book')
    user_id = Column(Integer, ForeignKey('Users.id', ondelete='CASCADE'))

    def __repr__(self):
        return "<Book('%d', '%s','%s')>" % (self.id, self.name, self.author)


class UserProgress(Base):
    __tablename__ = 'UsersProgress'

    user_id = Column(ForeignKey('Users.id'), primary_key=True)
    book_id = Column(ForeignKey('Books.id'), primary_key=True)
    page = Column(Integer(), nullable=False)

    def __repr__(self):
        return "<UserProgress(user_id=%d, book_id=%d, page=%d)>" % (self.user_id, self.book_id, self.page)


class Page(Base):
    __tablename__ = 'Pages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer)
    book_id = Column(Integer, ForeignKey('Books.id', ondelete='CASCADE'))
    data = Column(LargeBinary(2 ** 20))

    def __repr__(self):
        return "<Page('%s','%s', 'len(%d)')>" % (self.number, self.book_id, len(self.data))
