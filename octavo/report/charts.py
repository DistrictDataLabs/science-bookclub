# octavor.report.charts
# Create matplotlib charts for our reports
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Apr 11 17:12:51 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: charts.py [] benjamin@bengfort.com $

"""
Create matplotlib charts for our reports
"""

##########################################################################
## Imports
##########################################################################

import numpy
import pylab

from octavo.recommend.similarity import ReviewerSimilarity

class PreferenceGraph(object):

    similarity = ReviewerSimilarity()

    def plot(self, criticA, criticB):
        """
        Plot shared preferences as a scatter plot
        """
        preferences = self.similarity.shared_preferences(criticA, criticB)
        print preferences

        # Yank out the arrays of x and y values for each critic.
        x = [pref[0] for pref in preferences.values()]
        y = [pref[1] for pref in preferences.values()]

        # Scatter plot from points
        pylab.plot(x, y, 'r*')

        # Add Best fit line
        fit = pylab.polyfit(x,y,1)
        fit_fn = pylab.poly1d(fit)
        pylab.plot(xrange(0,7), fit_fn(xrange(0,7)), '--k')

        # Set chart properties
        pylab.title("%s and %s's %i mutually ranked items." % (criticA, criticB, len(preferences)))
        pylab.xlabel(criticA)
        pylab.ylabel(criticB)
        pylab.xlim(0.0, 6.0)
        pylab.ylim(0.0, 6.0)

        pylab.show()

if __name__ == '__main__':
    grapher = PreferenceGraph()
    grapher.plot(8398291, 4527753)
