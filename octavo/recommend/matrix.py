# octavo.recommend.matrix
# A Recommendation Model built on an internal Recommendations Matrix
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  timestamp
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: matrix.py [] benjamin@bengfort.com $

"""
A Recommendation Model built on an internal Recommendations Matrix
"""

##########################################################################
## Imports
##########################################################################

import time
import numpy
import pickle
import heapq

from factorization import *
from octavo.wrangle.models import *
from collections import defaultdict

##########################################################################
## Recommender Model
##########################################################################

class Recommender(object):
    """
    A recommender model
    """

    @classmethod
    def load(klass, pickle_path):
        """
        Load the Recommender object from a pickle.
        """
        with open(pickle_path, 'rb') as pkl:
            return pickle.load(pkl)

    def __init__(self, books=None, users=None):
        """
        Provide the books and users to build the recommender model around,
        if None is passed in, it is assumed that you use all books and all
        queries. This is a terrible idea.

        :param books: a list of ids of the books to build the recommender
        :param users: a list of ids of the users to build the recommender
        """
        self.books = books
        self.users = users
        self.model = None
        self.build_time = None
        self.build_date = None

    ##////////////////////////////////////////////////////////////////////
    ## Properties for easy access
    ##////////////////////////////////////////////////////////////////////

    @property
    def books(self):
        if not hasattr(self, '_books'):
            self._books = []
        return self._books

    @books.setter
    def books(self, value):
        if not value:
            session = create_session()
            value = list(b[0] for b in session.query(Book.id).order_by(Book.id))
            session.close()
        self._books = value

    @property
    def users(self):
        if not hasattr(self, '_users'):
            self._users = []
        return self._users

    @users.setter
    def users(self, value):
        if not value:
            session = create_session()
            value = list(u[0] for u in session.query(User.id).order_by(User.id))
            session.close()
        self._users = value

    @property
    def R(self):
        """
        Builds the training matrix
        """
        if not hasattr(self, '_R'):
            bumap = defaultdict(lambda: dict(map(lambda b: (b,0), self.books)))

            for uid in self.users:
                session = create_session()
                for review in session.query(Review).filter(Review.user_id==uid):
                    bumap[uid][review.book_id] = review.rating
                session.close()

            self._R = numpy.array(
                [
                    [bmap[bid] for bid in self.books]
                    for bmap in [bumap[uid] for uid in self.users]
                ]
            )
        return self._R

    ##////////////////////////////////////////////////////////////////////
    ## Helper methods
    ##////////////////////////////////////////////////////////////////////

    def cleanup(self):
        """
        Releases stored objects as an attempt to free up memory. Note that
        you may have to reinstantiate this class if you want the books and
        users mappings to regenerate.
        """
        del self._books
        del self._users

    def build_model(self):
        """
        Builds the parameterization array via non-negative matrix
        factorization - this could take a really long time!
        """
        start = time.time()
        nP, nQ     = nnmf(self.R)
        self.model = numpy.dot(nP, nQ.T)
        finit = time.time()
        self.build_time = finit - start

    def dump(self, pickle_path):
        """
        Dump this instance into a pickle for loading in the future.
        """
        with open(pickle_path, 'wb') as pkl:
            pickle.dump(self, pkl, pickle.HIGHEST_PROTOCOL)

    def sparsity(self):
        """
        Report the fraction of elements that are zero in the array
        """
        return 1 - self.density()

    def density(self):
        """
        Report the fraction of elements that are nonzero in the array
        """
        return float(numpy.count_nonzero(self.R)) / float(self.R.size)

    def guess_ratings(self, user):
        """
        Returns a book_id, estimated_rating for all unrated books for the
        given user. Note, other methods will have to be used to fetch.
        """
        useridx = self.users.index(user)
        for idx, rating in enumerate(self.model[useridx]):
            if self.R[useridx, idx] > 0:
                continue
            yield self.books[idx], rating

    def guess_picks(self, user, n=12, reverse=False):
        """
        Returns the top n picks. If reverse=True, then returns bottom n.
        """
        method  = heapq.nsmallest if reverse else heapq.nlargest
        session = create_session()
        picks   = method(n, self.guess_ratings(user), key=lambda t: t[1])
        return [(session.query(Book).get(bid), est) for bid,est in picks]

if __name__ == '__main__':

    # This is a terrible idea
    #recommender = Recommender()
    #recommender.build_model()
    #recommender.dump("reccod.pickle")
    #print "Training took %0.3f seconds" % recommender.build_time

    recco = Recommender.load('fixtures/reccod.pickle')
    ratings = recco.guess_picks(8398291)
    for b, r in ratings:
        print "%0.3f: %s" % (r, b)
