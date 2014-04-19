# octavo.recommend.similarity
# Computes similarity scores for the recommender
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Apr 10 10:34:23 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: similarity.py [] benjamin@bengfort.com $

"""
Computes similarity scores for the recommender
"""

##########################################################################
## Imports
##########################################################################

import operator

from math import sqrt
from collections import defaultdict
from octavo.wrangle.models import *

##########################################################################
## Similarity Base
##########################################################################

class SimilarityBase(object):
    """
    Base class for similarity computation. This base class provides access
    to the database
    """

    @property
    def session(self):
        """
        Returns a database session object and stores it on the object
        for future use, to ensure the connection is available when needed.
        """
        if not self.is_connected():
            self.connect()
        return self._session

    def connect(self):
        """
        Creates the session/connection to the database.
        """
        self._session = create_session()

    def close(self, commit=False):
        """
        Closes the connection to the database, commiting changes if asked.
        """
        if not self.is_connected(): return
        if commit: self._session.commit()
        self._session.close()
        self._session = None

    def is_connected(self):
        """
        Checks if the Similarity object is connected to the DB.
        """
        return hasattr(self, '_session') and not self._session is None

    def _compute_rank(self, metric, critic):

        if not callable(metric):
            raise TypeError("The 'metric' argument must be callable.")

        similarities = {}
        for user in self.session.query(User).filter(User.id!=critic).all():
            similarities[user.name] = metric(critic, user.id)

        return sorted(similarities.items(), key=operator.itemgetter(1), reverse=True)

    def euclidean_distance(self, objA, objB):
        """
        Reports the Euclidean distance of two critics, A and B by
        performing a J-dimensional Euclidean calculation of each of their
        preference vectors for the intersection of books the critics have
        rated.
        """

        # Get the intersection of the rated titles in the data.
        preferences = self.shared_preferences(objA, objB)

        # If they have no rankings in common, return 0.
        if not preferences or len(preferences) == 0: return 0

        # Sum the squares of the differences
        sum_of_squares = sum([pow(a-b, 2) for a, b in preferences.values()])

        # Return the inverse of the distance to give a higher score to
        # folks who are more similar (e.g. less distance) add 1 to prevent
        # division by zero errors and normalize ranks in [0, 1]
        return 1 / (1 + sqrt(sum_of_squares))

    def euclidean_rank(self, obj):
        return self._compute_rank(self.euclidean_distance, obj)

    def pearson_correlation(self, objA, objB):
        """
        Returns the Pearson Correlation of two critics, A and B by
        performing the PPMC calculation on the scatter plot of (a, b)
        ratings on the shared set of critiqued titles.
        """

        # Get the set of mutually rated items
        preferences = self.shared_preferences(objA, objB)

        # Store the length to save traversals of the len computation.
        # If they have no rankings in common, return 0.
        if not preferences or len(preferences) == 0: return 0
        length = len(preferences)

        # Loop through the preferences of each critic once and compute the
        # various summations that are required for our final calculation.
        sumA = sumB = sumSquareA = sumSquareB = sumProducts = 0
        for a, b in preferences.values():
            sumA += a
            sumB += b
            sumSquareA  += pow(a, 2)
            sumSquareB  += pow(b, 2)
            sumProducts += a*b

        # Calculate Pearson Score
        numerator   = (sumProducts*length) - (sumA*sumB)
        denominator = sqrt(((sumSquareA*length) - pow(sumA, 2))
                            * ((sumSquareB*length) - pow(sumB, 2)))

        # Prevent division by zero.
        if denominator == 0: return 0

        return abs(numerator / denominator)

    def pearson_rank(self, obj):
        return self._compute_rank(self.pearson_correlation, obj)

    def shared_preferences(self, objA, objB):
        """
        Should return a preference dictionary whose keys are a reference
        to the preference and whose values are a tuple of the preference
        values for (objA, objB) respectively. In the case of user ratings
        for books, the preferences should be in the form:

            {
                'book title': (ratingA, ratingB)
            }


        """
        raise NotImplementedError("Subclasses must aquire shared shared preferences!")


class ReviewerSimilarity(SimilarityBase):

    def shared_preferences(self, criticA, criticB):
        """
        Pass in a userid for right now...
        Returns shared preferences for the critic.
        """

        def shared(item):
            return len(item[1]) > 1

        prefs = defaultdict(dict)
        query = self.session.query(Review)
        query = query.filter(Review.user_id.in_([criticA, criticB]))
        query = query.filter(Review.rating!=0)

        for review in query.all():
            prefs[review.book_id][review.user_id] = review.rating

        return dict((k, v.values()) for k,v in filter(shared, prefs.items()))

