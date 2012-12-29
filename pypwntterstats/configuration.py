import yaml
from datetime import datetime, date, time, timedelta


class Configuration():
    """Set's up the configuration based on a file and
    some defaults coded here"""

    DEFAULT_USER = "xurxosanz"
    fromDate = datetime.combine(date.today() + timedelta(days=-1), time(0, 0))
    toDate = datetime.combine(date.today() + timedelta(days=-1), time(23, 59, 59))

    def __init__(self, configFile="config.yml"):
        self.configFile = configFile

        try:
            with self.configFile as f:
                self.data = yaml.load(f.read())
        except Exception, e:
            raise e

    def setUpDateLimits(self, fromDate, toDate):
        if toDate:
            self.toDate = datetime.combine(toDate, time(23, 59, 59))

        if fromDate:
            self.fromDate = datetime.combine(fromDate, time(0, 0))

        if fromDate > toDate:
            raise UserWarning("Dates provided ar wrong, please review")
