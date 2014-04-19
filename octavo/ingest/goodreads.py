# octavo.ingest.goodreads
# Python handler for the Goodreads API
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Mar 31 09:56:14 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: goodreads.py [] benjamin@bengfort.com $

"""
Python handler for the Goodreads API.

We're most interested in Reviews data, but this API ingestor can be used
to fetch and store any data from Goodreads. Here is an example URL:

    https://www.goodreads.com/review/list?format=xml&v=2&id=8398291

Note that the Goodreads API Key is required to see this data.
"""

##########################################################################
## Imports
##########################################################################

import os
import re
#import shutil          # Used if downloaded to a tempfile then moved
#import tempfile        # Used if downloaded to a tempfile then moved
import requests

from urllib import urlencode
from octavo.config import settings
from urlparse import urlsplit, urlunsplit

##########################################################################
## API Handler
##########################################################################

class Goodreads(object):
    """
    Fetches data from the Goodreads API and stores it on disk.
    """

    HOST = "https://www.goodreads.com"

    APIM = {
        'author.show':  '/author/show.xml',      # Get info about an author
        'book.show':    '/book/show',            # Get reviews for a book
        'reviews.list': '/review/list',          # Get reviews for a user
        'user.show':    '/user/show',            # Get info about a user
    }

    def __init__(self, host=None, apikey=None, secret=None, htdocs=None):
        self.host   = host or self.HOST
        self.apiurl = urlsplit(self.host)
        self.apikey = apikey or settings.get('goodreads_access_key')
        self.secret = secret or settings.get('goodreads_secret_key')
        self.htdocs = htdocs or settings.get('htdocs')

    def encode_params(self, params, key=True):
        """
        Encodes the parameters and adds the key if requested.
        """
        if key: params.update({'key': self.apikey})
        return urlencode(params)

    def construct_endpoint(self, method, params, key=True):
        """
        Constructs an API endpoint from the API method with the parameters
        that are necessary for retreiving the endpoint. This will also
        join the key to the parameters unless key=False is in the kwargs.

        Note that the method must be a correct API method from the absolute
        URI of the Goodreads API (e.g. reviews.xml vs reviews/list)
        """
        params = self.encode_params(params, key=key)
        return urlunsplit((self.apiurl.scheme, self.apiurl.netloc, method, params, ''))

    def request(self, method, params, action='get', **kwargs):
        """
        Retrieves a data from the goodreads API after constructing the API
        endpoint. Utilizes the action, which should be GET, POST, PUT, etc.
        Headers, etc. can be passed in as kwargs to the request method.
        """
        require_key = kwargs.pop('key', True)
        endpoint    = self.construct_endpoint(method, params, require_key)

        action = action.lower()
        if hasattr(requests, action):
            action = getattr(requests, action)
            if callable(action):
                return action(endpoint, **kwargs)
        raise AttributeError('No HTTP method "%s"' % action)

    def fetch(self, method, params, filename, action='get', **kwargs):
        """
        Fetches data from the API and then writes it to disk in the htdocs
        folder that was passed in as a parameter to this ingestor. Note
        that this uses the stream method so that the whole content isn't
        loaded into memory, but is rather iterated in chunks.

        Good practice here is to download to a temporary file then move
        the tempfile to the location specified.
        """
        response = self.request(method, params, action=action, stream=True, **kwargs)
        filepath = os.path.join(self.htdocs, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return filepath

    def batch_fetch(self, method, params, filename, action='get', **kwargs):
        """
        Handles pagination in API requests by issuing many requests with
        some parameters and saving the results to seperate files. The batch
        parameters must be stored in kwargs.
        """
        page_key     = kwargs.pop('page_key', 'page')           # Specifies parameter that gets particular page
        per_page_key = kwargs.pop('per_page_key', 'per_page')   # Specifies parameter that sets the results per page
        per_page     = kwargs.pop('per_page', 200)              # Specifies how many results to fetch at a time
        total        = kwargs.pop('total', 0)                   # Specifies how many rsults are expected
        pages        = (total / per_page) +1                    # Total number of pages we'll have to fetch
        name, ext    = os.path.splitext(filename)               # Save multiple files with page number
        stored       = []                                       # Store filenames where we saved files to.

        params.update({per_page_key:per_page})                  # Update parameters with per page info

        for idx in xrange(1, pages+1):
            params.update({page_key: idx})
            filename = "%s-%03d%s" % (name, idx, ext)
            stored.append(self.fetch(method, params, filename, action=action, **kwargs))

        return stored

    def reviews(self, userid, filename=None, batch=False, **kwargs):
        """
        Fetches the reviews for the given user, with any kwargs being
        parameters to the API Method. If you need to pass kwargs to the
        request, then this method is too general.

        If filename is given, then this method will return the path where
        the reviews data was saved to (using fetch). Otherwise it will
        return the response object from the request method.

        If batch is True, then this method will attempt to collect all the
        reviews by requesting an in-memory review request of one item, and
        inspecting it for the total number of reviews. Note that batch
        requires a filename, multiple responses will not be returned.
        """

        def batch_reviews(method, query, filename):
            """
            An internal helper method that does a lookup and inspection of
            a simple review object to fetch all pages of the reviews.

            This isn't extensible- but we can point out we can move this on
            later when we know more about how our system will use the API.
            """
            query.update({'per_page': 1, 'page': 1})
            response = self.request(method, query)

            # simple search for the total number of reviews.
            search = re.compile(r'<reviews start="\d+" end="\d+" total="(\d+)">')
            match  = re.search(search, response.text)
            if not match:
                raise Exception("Could not find total for batch request")
            total = int(match.groups()[0])

            return self.batch_fetch(method, query, filename, total=total)

        # Query params for the reviews endpoint
        query = {
            'v': 2,
            'id': userid,
            'format': 'xml',
            'sort': 'rating',
            'order': 'd',
        }
        query.update(kwargs)                    # Update passed in params
        method = self.APIM['reviews.list']      # Fetch the review list method

        if filename:
            if batch:
                return batch_reviews(method, query, filename)
            return self.fetch(method, query, filename)
        return self.request(method, query)

if __name__ == '__main__':
    api = Goodreads()
    print api.reviews(userid=8398291, filename='8398291-reviews.xml', batch=True)

