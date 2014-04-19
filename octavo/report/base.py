# octavo.report.base
# Base object for the creation of Reports
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Apr 17 10:13:50 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: base.py [] benjamin@bengfort.com $

"""
Base object for the creation of Reports
"""

##########################################################################
## Imports
##########################################################################

from jinja2 import Environment, PackageLoader

##########################################################################
## Report Object
##########################################################################

class Report(object):
    """
    Base class that wraps the templating language in a Django-like way.
    """

    template_name = None

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    @property
    def environment(self):
        """
        The Jinja2 Environment and Template loader
        """
        if not hasattr(self, '_environment'):
            loader = PackageLoader('octavo.report', 'templates')
            self._environment = Environment(loader=loader)
        return self._environment

    def render(self, path, **kwargs):
        """
        Renders the report with the template and context data to a file.
        """
        context  = self.get_context_data(**kwargs)
        template = self.get_template()
        template.stream(context).dump(path)

    def get_template(self):
        """
        Uses Jinja2 to fetch the template from the Environment
        """
        if self.template_name is None:
            raise Exception("Report requires either a definition of "
                            "template_name or implementation of get_template")
        return self.environment.get_template(self.template_name)

    def get_context_data(self, **kwargs):
        """
        Construct context data on a per report basis to render the report.
        """
        if 'report' not in kwargs:
            kwargs['report'] = self
        return kwargs

if __name__ == '__main__':
    report = Report(template_name='base.html')
    report.render('report.html', title='Test Report')
