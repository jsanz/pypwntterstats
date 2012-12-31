# -*- coding: utf-8 -*-

import json
from operator import __add__
from cStringIO import StringIO
from jinja2 import Template, Environment, PackageLoader
from datetime import datetime
from unidecode import unidecode
import locale
import re
import operator
import string


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

    def printBusiest(self, number):
        self.data["busiest"] = self.db.getTweetsPerUser(self.config.fromDate,
                                    self.config.toDate, number)

    def printHashtags(self, number, cloud):
        data = self.db.getHashTags(self.config.fromDate, self.config.toDate)

        ##extract individual hashtags
        hashtags = {}

        # get a complete list of tags
        for twit in data:
            text = twit[0]
            tags = [result for result in re.findall('(#[A-Za-z0-9]+)*', text) if len(result) > 0]
            for tag in tags:
                if tag in hashtags:
                    hashtags[tag] += 1
                else:
                    hashtags[tag] = 1

        sortedTags = sorted(hashtags.iteritems(), key=operator.itemgetter(1))[max(number, cloud) * -1:]
        cloudTags = sorted(sortedTags, key=lambda (a, b): a.lower().replace("#", ""))
        sortedTags.reverse()
        self.data["hashtags"] = sortedTags[0:number]
        self.data["cloudtags"] = cloudTags[0:cloud]
        print "{} of {} hashtags reported".format(len(self.data["hashtags"]), len(hashtags))

    def printWords(self, number, cloud):
        data = self.db.getTweets(self.config.fromDate, self.config.toDate)

        ##extract individual hashtags
        words = {}

        # get a complete list of tags
        for twit in data:
            text = twit[0]
            tags = [result for result in self.__split(text)]
            for tag in tags:
                if tag in words:
                    words[tag] += 1
                else:
                    words[tag] = 1

        sortedWords = sorted(words.iteritems(), key=operator.itemgetter(1))[max(number, cloud) * -1:]
        cloudWords = sorted(sortedWords, key=lambda (a, b): a.lower().replace("#", ""))
        sortedWords.reverse()
        self.data["words"] = sortedWords[0:number]
        self.data["cloudwords"] = cloudWords[0:cloud]
        print "{} of {} hashtags reported".format(len(self.data["words"]), len(words))

    def printReport(self):
        """Get the string from the delegate and print it on a file"""
        self.config.file.write(self.getRawString())
        self.config.file.close()

    def __split(self, text):
        """Function to tokenize a text removing unwanted texts"""

        ## TODO: borrar stopwords, enlaces, menciones, hashtags, puntuacion
        return string.split(unidecode(text))


class JSONOutput(Output):
    """Produces a JSON output"""
    name = "json"

    class DateEncoder(json.JSONEncoder):
        """Class to be able to encode in JSON dates using ISO 8601 format"""
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat(" ")
            return json.JSONEncoder.default(self, obj)

    def getRawString(self):
        file_str = StringIO()
        try:
            isJSONP = self.config.data["output"]["json"]["jsonp"]
            if isJSONP:
                try:
                    callback = self.config.data["output"]["json"]["callback"]
                except AttributeError:
                    callback = "callback"
        except AttributeError:
            isJSONP = False

        if isJSONP:
            file_str.write('{}('.format(callback))
        json.dump(self.data, file_str, indent=2, cls=self.DateEncoder)
        if isJSONP:
            file_str.write(');')
        return file_str.getvalue()


class HTMLOutput(Output):
    """Produces a basic HTML output"""
    name = "html"

    def __getJinjaEnvironment(self):
        env = Environment(loader=PackageLoader('pypwntterstats.output', 'templates'))

        def strFormat(value, format='{:.<30}'):
            return format.format(value)

        def prettyInt(value):
            locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
            return locale.format("%d", value, grouping=True)

        env.filters['strFormat'] = strFormat
        env.filters['unidecode'] = unidecode
        env.filters['prettyint'] = prettyInt

        return env

    def getRawString(self):
        """Renders the data using template, provided at the config or
        using the default provided by the package"""

        env = self.__getJinjaEnvironment()

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
