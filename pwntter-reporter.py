#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" To load this from a python sesion run %run pwntter-reporterp.py and paste:

from pypwntterstats import *
from pypwntterstats.output import *
args = Arguments(getArgs(config='myconfig.yml')).args
c = Configuration(args)
db = Database(c.data["db"])
outputReport = OutputProvider(c, db).getOutput()

An then for example:

db.getTweets(c.fromDate,c.toDate)[0]

to get the first tweet on the complete tweet texts query
"""

from pypwntterstats import *
from pypwntterstats.output import *
from pypwntterstats.arguments import fromDateToInt

import sys
import datetime
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def getArgs(config='config.yml', isQuuiet="true", user="xurxosanz",
            output="output.html", format="json",
            fromDate=datetime.date.today() + datetime.timedelta(days=-1),
            toDate=datetime.date.today() + datetime.timedelta(days=-1)):
    return [
            "-o", output, "-f", format, "-c", config,
            "-u", user, "-F", fromDateToInt(fromDate),
            "-T", fromDateToInt(fromDate)
            ]


def main(args):
    """Process the main call, reading the arguments and next the
    configuration file"""

    """Read the configuration if it exists"""
    c = Configuration(args)

    """Do the stuff"""
    # Say what is going to happen
    if not c.quiet:
        logging.info("Running in verbose mode")
        logging.info("Using {} file".format(c.configFile.name))
        logging.info("Writing {} report in {} for @{}".format(c.format, c.file.name, c.user))
        logging.info("From {}".format(c.fromDate))
        logging.info("To {}".format(c.toDate))

    #Set up database connection and mappings
    db = Database(c.data["db"])

    #Get a format specific output
    outputReport = OutputProvider(c, db).getOutput()

    #Generate the stats specified at config
    outputReport.doStats(c.data["stats"])

    # Print the results
    outputReport.printReport()

if __name__ == "__main__":
    sys.exit(main(Arguments().args))
