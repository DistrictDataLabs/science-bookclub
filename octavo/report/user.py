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
from octavo.wrangle.models import *

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
        super(UserReport, self).__init__(**kwargs)

    def recommender_status(self):
        """
        Returns the general status of the recommender
        """
        return {
            'status': {
                'reviews': self.session.query(Review).count(),
                'books': self.session.query(Book).count(),
                'users': self.session.query(User).count(),
            }
        }

    def get_context_data(self, **kwargs):
        # Set the defaults for the context
        context = {
            'title': 'Recommendations for %s' % str(self.user),
            'user': self.user,
        }

        context.update(self.recommender_status())       # Update general status
        context.update(kwargs)                          # Update from args

        return context

if __name__ == '__main__':
    report = UserReport(8398291)
    report.render('benjamin.html')
