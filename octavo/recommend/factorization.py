# octavo.recommend.factorization
# Performs Matrix Factorization for the recommender
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Apr 16 11:37:17 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: factorization.py [] benjamin@bengfort.com $

"""
Performs Matrix Factorization for the recommender
http://www.quuxlabs.com/blog/2010/09/matrix-factorization-a-simple-tutorial-and-implementation-in-python/
"""

##########################################################################
## Imports
##########################################################################

import time
import numpy
import pickle

from octavo.wrangle.models import *
from collections import defaultdict

##########################################################################
## Factorization
##########################################################################

def initialize(R, K):
    """
    Returns initial matrices for an N X M matrix, R and K features.

    :param R: the matrix to be factorized
    :param K: the number of latent features

    :returns: P, Q initial matrices of N x K and M x K sizes
    """
    N = len(R)
    M = len(R[0])
    P = numpy.random.rand(N,K)
    Q = numpy.random.rand(M,K)

    return P, Q

def nnmf(R, P=None, Q=None, K=2, steps=5000, alpha=0.0002, beta=0.02):
    """
    Performs matrix factorization on R with given parameters.

    :param R: A matrix to be factorized, dimension N x M
    :param P: an initial matrix of dimension N x K
    :param Q: an initial matrix of dimension M x K
    :param K: the number of latent features
    :param steps: the maximum number of iterations to optimize in
    :param alpha: the learning rate for gradient descent
    :param beta:  the regularization parameter

    :returns: final matrices P and Q
    """

    if not P or not Q:
        P, Q = initialize(R, K)

    Q = Q.T
    for step in xrange(steps):
        for idx in xrange(len(R)):
            for jdx in xrange(len(R[idx])):
                if R[idx][jdx] > 0:
                    eij = R[idx][jdx] - numpy.dot(P[idx,:], Q[:,jdx])
                    for kdx in xrange(K):
                        P[idx][kdx] = P[idx][kdx] + alpha * (2 * eij * Q[kdx][jdx] - beta * P[idx][kdx])
                        Q[kdx][jdx] = Q[kdx][jdx] + alpha * (2 * eij * P[idx][kdx] - beta * Q[kdx][jdx])

        eR = numpy.dot(P,Q)
        e  = 0

        for idx in xrange(len(R)):
            for jdx in xrange(len(R[idx])):
                if R[idx][jdx] > 0:
                    e = e + pow(R[idx][jdx] - numpy.dot(P[idx,:], Q[:,jdx]), 2)
                    for k in xrange(K):
                        e = e + (beta/2) * (pow(P[idx][kdx], 2) + pow(Q[kdx][jdx], 2))
        if e < 0.001:
            break

    return P, Q.T

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
            pickle.dump(self, pkl)

if __name__ == '__main__':

    #This is the Test case. Expected output is available.
#    R = numpy.array([
#            [5,3,0,1],
#            [4,0,0,1],
#            [1,1,0,5],
#            [1,0,0,4],
#            [0,1,5,4],
#        ])

#    nP, nQ = nnmf(R)
#    nR = numpy.dot(nP, nQ.T)
#    print nR

    # This is a terrible idea
    recommender = Recommender()
    recommender.build_model()
    recommender.dump("reccod.pickle")
    print "Training took %0.3f seconds" % recommender.build_time
