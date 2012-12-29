#!/usr/bin/env python
# -*- coding: utf-8 -*-


from pypwntterstats import *
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

    db = Database(c.data["db"])

    outputReport = OutputProvider(c, db).getOutput()

    if c.data["general"] and c.data["general"]["print"]:
        if not c.quiet:
            print "Getting general stats"
        outputReport.printGeneral()

    if c.data["clients"] and c.data["clients"]["print"]:
        if not c.quiet:
            print "Getting client count stats ({} or more)".format(c.data["clients"]["minimum"])
        outputReport.printClients(c.data["clients"]["minimum"])

    # Print the results

    outputReport.printReport()

if __name__ == "__main__":
    sys.exit(main())
