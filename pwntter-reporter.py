#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pypwntterstats import *
from pypwntterstats.output import *
import sys




def main():
    """Process the main call, reading the arguments and next the
    configuration file"""

    """Process the arguments"""
    args = Arguments().args

    """Read the configuration if it exists"""
    c = Configuration(configFile=args.config)

    """Do the stuff"""
    # Assign arguments to complete config
    c.quiet = args.quiet
    c.user = args.user
    c.file = args.output
    c.format = args.format
    c.setUpDateLimits(args.FROM, args.TO)

    # Say what is going to happen
    if not c.quiet:
        print "Running in verbose mode"
        print "Using {} file".format(c.configFile.name)
        print "Writing {} report in {} for @{}".format(c.format, c.file.name, c.user)
        print "From {}".format(c.fromDate)
        print "To {}".format(c.toDate)

    db = Database(c.data["db"])

    outputReport = OutputProvider(c, db).getOutput()

    # Print general data
    try:
        if c.data["general"] and c.data["general"]["print"]:
            if not c.quiet:
                print "Getting general stats"
            outputReport.printGeneral()
    except KeyError:
        print "No general data"

    # Print client statistics
    try:
        if c.data["clients"] and c.data["clients"]["print"]:
            if c.data["clients"] and c.data["clients"]["minimum"]:
                clientes_minimum = c.data["clients"]["minimum"]
            else:
                clientes_minimum = c.DEFAULTS["clients"]["minimum"]
            if not c.quiet:
                print "Getting client count stats ({} or more)".format(clientes_minimum)
            outputReport.printClients(clientes_minimum)
    except KeyError:
        print "No clients data"

    # Print tweets per user
    try:
        if c.data["busiest"] and c.data["busiest"]["print"]:
            if c.data["busiest"] and c.data["busiest"]["number"]:
                busiest_number = c.data["busiest"]["number"]
            else:
                busiest_number = c.DEFAULTS["busiest"]["number"]
            if not c.quiet:
                print "Getting users tweets count stats ({})".format(busiest_number)
            outputReport.printBusiest(busiest_number)
    except KeyError:
        print "No busiest data"

    # Print hashtags
    try:
        if c.data["hashtags"] and c.data["hashtags"]["print"]:
            if c.data["hashtags"] and c.data["hashtags"]["number"]:
                hashtags = c.data["hashtags"]["number"]
            else:
                hashtags = c.DEFAULTS["hashtags"]["number"]

            if c.data["hashtags"] and c.data["hashtags"]["cloud"]:
                htcloud = c.data["hashtags"]["cloud"]
            else:
                htcloud = c.DEFAULTS["hashtags"]["cloud"]

            if not c.quiet:
                print "Getting hashtags stats ({})".format(hashtags)
            outputReport.printHashtags(hashtags, htcloud)
    except KeyError:
        print "No hashtags data"

    # Print Words
    try:
        if c.data["words"] and c.data["words"]["print"]:
            if c.data["words"] and c.data["words"]["number"]:
                words = c.data["words"]["number"]
            else:
                words = c.DEFAULTS["words"]["number"]

            if c.data["words"] and c.data["words"]["cloud"]:
                wcloud = c.data["words"]["cloud"]
            else:
                wcloud = c.DEFAULTS["words"]["cloud"]

            if not c.quiet:
                print "Getting words stats ({})".format(words)
            outputReport.printWords(words, wcloud)
    except KeyError:
        print "No hashtags data"
    # Print the results
    outputReport.printReport()

if __name__ == "__main__":
    sys.exit(main())
