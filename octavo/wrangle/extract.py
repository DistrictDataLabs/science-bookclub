# octavo.wrangle.extract
# Extract data from xml files downloaded by ingestor
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Mar 31 17:37:59 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: extract.py [] benjamin@bengfort.com $

"""
Extract data from xml files downloaded by ingestor
"""

##########################################################################
## Imports
##########################################################################

from datetime import date
from bs4 import BeautifulSoup

##########################################################################
## REview Object
##########################################################################

class Review(object):
    """
    Internal review object that wraps BS4 tag and provides helpful methods
    to get data out of the xml element.
    """

    def __init__(self, review):
        self.element = review

    @property
    def title(self):
        return self.element.book.title.text

    @property
    def rating(self):
        return int(self.element.rating.text)

    def get_book_data(self):
        """
        Returns a dictionary of values to populate a book entity table for
        our recommender system. These values will be saved in our database.
        """
        book = self.element.book
        return {
            "id": int(book.id.text),
            "title": book.title.text,
            "image": book.image_url.text,
            "link": book.link.text,
            "pages": int(book.num_pages.text) if book.num_pages.text else None,
            "published": int(book.published.text) if book.published.text else None,
            "description": book.description.text,
        }

    def get_author_data(self):
        """
        Returns a list of dictionary values for author data to store.
        """
        for author in self.element.authors.find_all('author'):
            yield {
                "id":   int(author.id.text),
                "name": author.find('name').text,   # Name is the tag name in BS4...
            }

    def get_book_authors_data(self):
        """
        Returns the many to many mapping of books to authors.
        """
        for author in self.get_author_data():
            yield {
                "author_id": author["id"],
                "book_id":   int(self.element.book.id.text)
            }

    def get_book_reviews_data(self):
        """
        Returns the many to many mapping of book and review data.
        NOTE: We're missing the userid in this mapping
        """
        return {
            "user_id": None,
            "book_id": int(self.element.book.id.text),
            "rating":  self.rating,
        }

    def __str__(self):
        return "%s rated %i stars" % (self.title, self.rating)

##########################################################################
## ReviewExtractor
##########################################################################

class ReviewExtractor(object):
    """
    Wraps an XML parser to extract data particularly from each review in
    a Goodreads review.xml file. Uses BeautifulSoup to simply parsing.
    """

    def __init__(self, path):
        self.path   = path
        self.stream = None
        self.soup   = None

    def open(self):
        self.stream = open(self.path, 'rb')
        self.soup   = BeautifulSoup(self.stream, 'xml')

    def close(self):
        if self.stream: self.stream.close() # Release file handle
        if self.soup: self.soup.decompose() # Drop the XML out of memory
        self.stream = None                  # Force garbage collection
        self.soup   = None                  # Force garbage collection

    def __enter__(self):
        """
        Open a stream to the wrapped xml file and return the extractor for
        use in contextual with ... as statements (and ensure close).
        """
        self.open()
        return self

    def __exit__(self, type, value, tb):
        """
        Ensure any open streams are closed before exiting a context block.
        """
        self.close()

    def __iter__(self):
        if not self.soup: raise Exception("No handle to an xml soup object!")
        for review in self.soup.find_all('review'):
            yield Review(review)

##########################################################################
## Extractor "open-like function"
##########################################################################

extract = ReviewExtractor # Fun helper function alias

##########################################################################
## Test code for developer
##########################################################################

if __name__ == '__main__':
    with extract('fixtures/htdocs/25661442-001.xml') as extractor:
        for review in extractor:
            print review.get_book_reviews_data()
