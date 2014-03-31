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
import csv
import argparse

from octavo.ingest.goodreads import Goodreads

##########################################################################
## Command Line Variables
##########################################################################

DESCRIPTION = "An administrative utility for the Science bookclub"
EPILOG      = "If there are any bugs or concerns, please comment on Github"

##########################################################################
## Administrative Commands
##########################################################################

def ingest(args):
    """
    Ingests data from goodreads
    """

    if args.csvfile:
        print "Loading userids from %s" % args.csvfile.name
        reader = csv.DictReader(args.csvfile)
        args.userid.extend([int(row['id']) for row in reader])

    print "Fetching data from Goodreads"
    api = Goodreads(apikey=args.apikey, htdocs=args.htdocs)
    count = 0
    for userid in args.userid:
        fname = "%s.xml" % str(userid)
        paths = api.reviews(userid, fname, batch=args.batch)
        fmtst = "  fetched %s"

        if isinstance(paths, basestring): paths = [paths]
        for path in paths:
            count += 1
            print fmtst % path

    return "%i reviews downloaded to %s\n" % (count, api.htdocs)

##########################################################################
## Main Method
##########################################################################

def main(*argv):

    # Construct the argument parser
    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG)
    subparsers = parser.add_subparsers(title='commands', description='Administrative commands for Octavo')

    # Ingest Reviews Command
    ingest_parser = subparsers.add_parser('ingest', help='Collect the reviews for a Goodreads userid')
    ingest_parser.add_argument('--batch', action='store_true', default=False, help='force paginated download')
    ingest_parser.add_argument('--htdocs', type=str, default=None, help='set the download directory')
    ingest_parser.add_argument('--apikey', type=str, default=None, help='goodreads API key')
    ingest_parser.add_argument('--bulk-ingest', metavar='PATH', dest='csvfile', type=argparse.FileType('r'),
                               required=False, help='Bulk load from CSV file')
    ingest_parser.add_argument('userid', type=int, nargs='*', help='userid to collect reviews for')
    ingest_parser.set_defaults(func=ingest)

    # Handle input from the command line
    args = parser.parse_args()            # Parse the arguments
    try:
        msg = args.func(args)             # Call the default function
        parser.exit(0, msg)               # Exit clearnly with message
    except Exception as e:
        parser.error(str(e))              # Exit with error

if __name__ == '__main__':
    main(*sys.argv)
