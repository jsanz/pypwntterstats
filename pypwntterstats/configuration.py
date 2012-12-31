import yaml
from datetime import datetime, time


DEFAULTS = {
    'clients': {'minimum': 10},
    'busiest': {'number': 20},
    'hashtags': {'number': 20, 'cloud': 50},
    'words': {'number': 20, 'cloud': 50}
}


class Configuration():
    """Set's up the configuration based on a file and
    some defaults coded here"""

    def __init__(self, configFile=open("config.yml", 'r')):
        self.configFile = configFile

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
