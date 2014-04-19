# octavo.wrangle
# Data wrangling for Octavo App
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Mar 31 13:26:02 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
Data wrangling for Octavo App
"""

##########################################################################
## Imports
##########################################################################

import os
import heapq
import unicodecsv as csv

from models import *
from extract import extract
from sqlalchemy import desc
from sqlalchemy.sql import func

##########################################################################
## Wrangling
##########################################################################

def userid_from_path(path):
    """
    Helper function extracts a userid from a path
    """
    basename = os.path.basename(path)
    name,ext = os.path.splitext(basename)

    return name.split('-')[0]

def wrangle_users(path):
    """
    For a users CSV file, extracts and loads into database
    """
    session = create_session()
    with open(path, 'r') as data:
        reader = csv.DictReader(data)
        for row in reader:
            user = User(**row)
            user = session.merge(user)

    session.commit()
    session.close()

def wrangle_reviews(path, userid=None):
    """
    For a review xml file, extracts and loads into database
    """
    userid  = userid or userid_from_path(path)
    session = create_session()

    # Get user object
    user    = User(id=userid)
    user    = session.merge(user)

    with extract(path) as reviews:
        for review in reviews:
            book = Book(**review.get_book_data())
            book = session.merge(book)

            for author in review.get_author_data():
                author = Author(**author)
                author = session.merge(author)

            for data in review.get_book_authors_data():
                book_author = BookAuthor(**data)
                book_author = session.merge(book_author)

            review = review.get_book_reviews_data()
            review.update({'user_id': userid})
            review = Review(**review)
            review = session.merge(review)

    session.commit()
    session.close()

##########################################################################
## Some aggregations
##########################################################################

def popular_books(n=12, reverse=False):
    """
    Return most popular books. Give an nvalue for the n best books, use
    reverse to return the most hated books!
    """
    session = create_session()
    books   = session.query(Book)
    method  = heapq.nsmallest if reverse else heapq.nlargest
    return method(n, books, key=lambda b: b.average_rating())

def lazy_popular_books():
    """
    Returns a precomputed list of popular books.
    """
    session = create_session()
    bids = [2767052, 136251, 2657, 13496, 6148028, 7260188, 5, 5907, 10572, 16299, 62291, 8051458]
    for bid in bids:
        yield session.query(Book).get(bid)
