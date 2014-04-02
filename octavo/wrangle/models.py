# wrangle.models
# SQLAlchemy models using the declarative extenstion
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Mar 31 22:54:08 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: models.py [] benjamin@bengfort.com $

"""
SQLAlchemy models using the declarative extenstion
"""

##########################################################################
## Imports
##########################################################################

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Unicode, UnicodeText
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from octavo.config import settings
from sqlalchemy import ForeignKey

##########################################################################
## Module Constants
##########################################################################

Base = declarative_base()  # SQLAlchemy declarative extension

##########################################################################
## Models
##########################################################################

class User(Base):

    __tablename__ = 'users'

    id            = Column(Integer, primary_key=True)
    name          = Column(Unicode(50))
    #reviews       = relationship("Review", secondary="Review")

class Book(Base):

    __tablename__ = 'books'

    id            = Column(Integer, primary_key=True)
    title         = Column(Unicode(255))
    image         = Column(Unicode(255))
    link          = Column(Unicode(255))
    pages         = Column(Integer)
    published     = Column(Integer)
    description   = Column(UnicodeText)
    authors       = relationship("Author", secondary="book_authors")
    #reviews       = relationship("Review", secondary="reviews")

class Author(Base):

    __tablename__ = 'authors'

    id            = Column(Integer, primary_key=True)
    name          = Column(Unicode(100))
    books         = relationship("Book", secondary="book_authors")

class BookAuthor(Base):

    __tablename__ = 'book_authors'

    book_id       = Column(Integer, ForeignKey('books.id'), primary_key=True)
    author_id     = Column(Integer, ForeignKey('authors.id'), primary_key=True)

class Review(Base):

    __tablename__ = 'reviews'

    book_id       = Column(Integer, ForeignKey('books.id'), primary_key=True)
    user_id       = Column(Integer, ForeignKey('users.id'), primary_key=True)
    rating        = Column(Integer, nullable=False)

##########################################################################
## Database helper methods
##########################################################################

def get_engine(uri=None):
    uri = uri or settings.get('database')
    uri = 'sqlite:///%s' % uri if uri else 'sqlite://'
    return create_engine(uri)

def create_session(eng=None):
    eng = eng or get_engine()
    return sessionmaker(bind=eng)()

def syncdb(uri=None):
    Base.metadata.create_all(get_engine(uri))
