# -*- coding: utf-8 -*-

import json
from operator import __add__
from cStringIO import StringIO
from jinja2 import Template, Environment, PackageLoader
from datetime import datetime
from unidecode import unidecode
import locale


class OutputProvider():
    """Class to provide an implementation"""

    def __init__(self, config, db):
        self.config = config
        self.db = db

    def getOutput(self):
        return {
            JSONOutput.name: lambda: JSONOutput(self.config, self.db),
            HTMLOutput.name: lambda: HTMLOutput(self.config, self.db)
        }[self.config.format]()


class Output():
    """Generic class to output reports"""
    data = dict()

    def __init__(self, config, db):
        self.config = config
        self.db = db

    def printGeneral(self):
        self.data["general"] = {"run": datetime.now(),
                                "from": self.config.fromDate,
                                "to": self.config.toDate,
                                "totalTweets": self.db.getTweetCount(self.config.fromDate,
                                                                       self.config.toDate)
                                }

    def printClients(self, config):
        """Produces an output of clients with count

        config: minimum number of tweets to print per client"""
        allData = self.db.getClientFrequencies(
                                    self.config.fromDate,
                                    self.config.toDate)

        over = [(data[0], data[1].decode("utf8")) for data in allData if data[0] >= config]
        below = [data[0] for data in allData if data[0] < config]
        countBelow = len(below)
        numBelow = reduce(__add__, below)
        others = (numBelow, '{} clients of {} or less'.format(countBelow, config - 1))

        self.data["clientCount"] = over + [others]

    def printReport(self):
        """Get the string from the delegate and print it on a file"""
        self.config.file.write(self.getRawString())
        self.config.file.close()


class JSONOutput(Output):
    """Produces a JSON output"""
    name = "json"

    def getRawString(self):
        file_str = StringIO()
        callback = "callback"
        try:
            callback = self.config.data["output"]["json"]["callback"]
        except AttributeError:
            pass

        file_str.write('{}('.format(callback))
        json.dump(self.data, file_str, indent=4)
        file_str.write(');')
        return file_str.getvalue()
        #self.config.file.write(file_str.getvalue())
        #self.config.file.close()


class HTMLOutput(Output):
    """Produces a basic HTML output"""
    name = "html"

    def getRawString(self):
        """Renders the data using template, provided at the config or
        using the default provided by the package"""

        env = Environment(loader=PackageLoader('pypwntterstats', 'templates'))

        def strFormat(value, format='{:.<30}'):
            return format.format(value)

        def prettyInt(value):
            locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
            return locale.format("%d", value, grouping=True)

        env.filters['strFormat'] = strFormat
        env.filters['unidecode'] = unidecode
        env.filters['prettyint'] = prettyInt

        try:
            """Try to search at the configuration"""
            templateFile = self.config.data["output"]["html"]["template"]
            with open(templateFile) as f:
                template = Template(f.read())
        except Exception:
            """If not found using a default"""
            template = env.get_template("template.html")

        try:
            toPrint = template.render(data=self.data)
            return toPrint.encode('utf-8')
        except Exception, e:
            raise e
