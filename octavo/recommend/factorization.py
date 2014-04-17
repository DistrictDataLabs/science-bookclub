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

import numpy

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
