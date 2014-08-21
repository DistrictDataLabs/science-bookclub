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
import time
import random
import argparse

from octavo.ingest.goodreads import Goodreads
from octavo.wrangle import wrangle_reviews as loaddb
from octavo.wrangle.models import syncdb as createdb
from octavo.recommend import Recommender
from octavo.report.user import UserReport

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
        try:
            fname = "%s.xml" % str(userid)
            paths = api.reviews(userid, fname, batch=args.batch)
        except:
            print "Error fetching reviews for user %s" % str(userid)
            continue

        fmtst = "  fetched %s"

        if isinstance(paths, basestring): paths = [paths]
        for path in paths:
            count += 1
            print fmtst % path

        time.sleep(random.randint(2,15))

    return "%i xml files downloaded to %s\n" % (count, api.htdocs)

def wrangle(args):
    """
    Load ingested data into the database
    """
    for review in args.reviews:
        if os.path.exists(review):
            loaddb(review)
    print "Loaded reviews from %i files" % len(args.reviews)

def syncdb(args):
    """
    Creates the database at the config location or specified location.
    """
    createdb(args.database)
    print "Database created."

def build(args):
    """
    Builds the model from the current database
    """
    print "Warning this is going to take hours..."
    print "Will write the model to '%s' once trained" % args.outpath[0]
    recommender = Recommender()
    recommender.build_model()
    recommender.dump(args.outpath[0])
    print "Training took %0.3f seconds" % recommender.build_time

def report(args):
    """
    Prints out a report for the particular user
    """
    report  = UserReport(args.user[0])
    outpath = args.outpath or '%s.html' % args.user[0]
    report.render(outpath)

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

    # Wrangle Reviews Command
    wrangle_parser = subparsers.add_parser('wrangle', help='Load review xml data into database')
    wrangle_parser.add_argument('reviews', type=str, nargs="+", help='Downloaded XML files to load')
    wrangle_parser.set_defaults(func=wrangle)

    # Syncdb command
    syncdb_parser = subparsers.add_parser('syncdb', help='Create the Sqlite3 database and load tables')
    syncdb_parser.add_argument('database', type=str, nargs='?', default=None, help='Path to create a sqlite3 database')
    syncdb_parser.set_defaults(func=syncdb)

    # Build model command
    build_parser = subparsers.add_parser('build', help='Builds the model from the current database')
    build_parser.add_argument('outpath', type=str, nargs=1, default='reccod.pickle', help='Path to write the model to.')
    build_parser.set_defaults(func=build)

    # Report command
    report_parser = subparsers.add_parser('report', help='Create an HTML report for the selected user')
    report_parser.add_argument('user', type=int, nargs=1, help='User id to write the report for')
    report_parser.add_argument('-o', '--outpath', type=str, default=None, help='Location to write report to')
    report_parser.set_defaults(func=report)

    # Handle input from the command line
    args = parser.parse_args()            # Parse the arguments
    try:
        msg = args.func(args)             # Call the default function
        parser.exit(0, msg)               # Exit clearnly with message
    except Exception as e:
        parser.error(str(e))              # Exit with error

if __name__ == '__main__':
    main(*sys.argv)
