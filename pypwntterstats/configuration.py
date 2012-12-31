import yaml
from datetime import datetime, time


class Configuration():
    """Set's up the configuration based on a file and
    some defaults coded here"""

    def __init__(self, args):
        self.configFile = args.config
        self.quiet = args.quiet
        self.user = args.user
        self.file = args.output
        self.format = args.format
        self.setUpDateLimits(args.FROM, args.TO)
        self.title = args.title or self.setUpTitle()

        try:
            with self.configFile as f:
                self.data = yaml.load(f.read())
        except Exception, e:
            raise e

    def setUpDateLimits(self, fromDate, toDate):
        if fromDate > toDate:
            raise UserWarning("Dates provided ar wrong, please review")

        self.fromDate = datetime.combine(fromDate, time(0))
        self.toDate = datetime.combine(toDate, time(23, 59, 59))

    def setUpTitle(self):
        res = "Twitter stats for "
        fromDate = "{:%Y/%m/%d}".format(self.fromDate)
        toDate = "{:%Y/%m/%d}".format(self.toDate)

        if fromDate == toDate:
            res = res + fromDate
        else:
            res = res + fromDate + " to " + toDate
        return res
