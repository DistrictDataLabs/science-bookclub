# tests.recommend_tests.factorization_tests
# Tests the factorization model in Octavo
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Apr 17 06:54:36 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: factorization_tests.py [] benjamin@bengfort.com $

"""
Tests the factorization model in Octavo
"""

##########################################################################
## Imports
##########################################################################

import numpy
import unittest

from octavo.recommend.factorization import *

##########################################################################
## Factorization TestCase
##########################################################################

class FactorizationTests(unittest.TestCase):

    def test_factorization(self):
        """
        Test the factorization function
        """

        #This is the Test case. Expected output is available.
        R = numpy.array([
                [5,3,0,1],
                [4,0,0,1],
                [1,1,0,5],
                [1,0,0,4],
                [0,1,5,4],
            ])

        nP, nQ = nnmf(R)
        M = numpy.dot(nP, nQ.T)

        for idx in xrange(len(R)):
            for jdx in xrange(len(R[0])):
                rij = R[idx][jdx]
                mij = M[idx][jdx]
                if rij > 0:
                    self.assertLess(abs(rij - mij), 0.25)
                else:
                    self.assertGreater(mij, 0)
