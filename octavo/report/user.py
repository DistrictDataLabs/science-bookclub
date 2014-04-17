# octavo.report.user
# Print out a per user recommendation report
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Apr 17 11:24:12 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: user.py [] benjamin@bengfort.com $

"""
Print out a per user recommendation report
"""

##########################################################################
## Imports
##########################################################################

from base import Report
from octavo.wrangle import lazy_popular_books as popular_books
from octavo.wrangle.models import *
from octavo.recommend import Recommender
from octavo.config import settings

##########################################################################
## User Report
##########################################################################

class UserReport(Report):
    """
    Prints out a per-user status report
    """

    template_name = 'user.html'

    def __init__(self, userid, **kwargs):
        self.session = create_session()
        self.user = self.session.query(User).get(userid)
        self.recommender = Recommender.load(settings.get('model_pickle'))
        super(UserReport, self).__init__(**kwargs)

    def system_status(self):
        """
        Returns the general status of the recommender
        """
        return {
            'status': {
                'reviews': self.session.query(Review).filter(Review.rating>0).count(),
                'books': self.session.query(Book).count(),
                'users': self.session.query(User).count(),
                'sparsity': self.recommender.sparsity() * 100,
                'build_time': self.recommender.build_time,
                'matrix_size': self.recommender.R.size,
            }
        }

    def get_context_data(self, **kwargs):
        # Set the defaults for the context
        context = {
            'title': 'Recommendations for %s' % str(self.user),
            'user': self.user,
            'popular': popular_books(), # Don't do this one in the demo
            'picks': self.recommender.guess_picks(self.user.id),
        }

        context.update(self.system_status())            # Update general status
        context.update(kwargs)                          # Update from args

        return context

if __name__ == '__main__':
    report = UserReport(8398291)
    report.render('benjamin.html')
