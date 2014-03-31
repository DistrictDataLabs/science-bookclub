#!/usr/bin/env python

# octavo-admin
# An administrative script for our bookclub
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Mar 30 20:26:20 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: octavo-admin.py [] benjamin@bengfort.com $

"""
An administrative script for our bookclub
"""

##########################################################################
## Imports
##########################################################################

import os
import sys
import argparse

##########################################################################
## Command Line Variables
##########################################################################

DESCRIPTION = "An administrative utility for the Science bookclub"
EPILOG      = "If there are any bugs or concerns, please comment on Github"

##########################################################################
## Main Method
##########################################################################

def main(*argv):

    # Construct the argument parser
    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG)

    # Add command line arguments
    # TODO

    # Parse the arguments from the commandline
    options = parser.parse_args()

if __name__ == '__main__':
    main(*sys.argv)
