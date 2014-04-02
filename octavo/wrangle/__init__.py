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
from models import *
from extract import extract

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

def wrangle(path, userid=None):
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
