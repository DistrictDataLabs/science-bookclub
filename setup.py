#!/usr/bin/env python
# setup
# Setup script for science-bookclub
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Mar 30 18:09:43 2014 -0400
#
# Copyright (C) 2014 District Data Labs
# For license information, see LICENSE.txt and NOTICE.md
#
# ID: setup.py [] benjamin@bengfort.com $

"""
Setup script for science-bookclub
"""

##########################################################################
## Imports
##########################################################################

try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    raise ImportError("Could not import \"setuptools\"."
                      "Please install the setuptools package.")

##########################################################################
## Package Information
##########################################################################

packages = find_packages(where=".", exclude=("tests", "bin", "docs", "fixtures",))
requires = []

with open('requirements.txt', 'r') as reqfile:
    for line in reqfile:
        requires.append(line.strip())

classifiers = (
    # TODO: Add classifiers
    # See: https://pypi.python.org/pypi?%3Aaction=list_classifiers
)

config = {
    "name": "ScienceBookclub",
    "version": "0.1",
    "description": "Generating the next read for our book club- with Data Science!",
    "author": "Benjamin Bengfort",
    "author_email": "bb830@georgetown.edu",
    "url": "https://github.com/DistrictDataLabs/science-bookclub",
    "packages": packages,
    "install_requires": requires,
    "classifiers": classifiers,
    "zip_safe": False,
    "scripts": [],
}

##########################################################################
## Run setup script
##########################################################################

if __name__ == '__main__':
    setup(**config)
