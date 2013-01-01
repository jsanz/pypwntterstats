# -*- coding: utf-8 -*-

import json
from operator import __add__
from cStringIO import StringIO
from jinja2 import Environment, PackageLoader
from datetime import datetime
from unidecode import unidecode
import locale
import re
import operator
import codecs
import logging


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
    DEFAULTS = {
        'clients': {'minimum': 10},
        'busiest': {'number': 20},
        'hashtags': {'number': 20, 'cloud': 50},
        'words': {'number': 20, 'cloud': 50, 'stopwords': 'stopwords.txt'}
    }

    data = dict()

    def __init__(self, config, db):
        self.config = config
        self.db = db
        self.data["title"] = config.title

    def doStats(self, config):
        """Iterates over configuration trying to execute a method for every
           confi item using introspection"""
        for stat in config:
            try:
                if config[stat]["print"]:
                    # merge the defaults an this config
                    if stat in self.DEFAULTS:
                        toolConfig = dict(self.DEFAULTS[stat].items() + config[stat].items())
                    else:
                        toolConfig = config[stat]
                    # call the new method
                    getattr(self, "print_{}".format(stat))(toolConfig)
                else:
                    logging.debug("Skipping {}".format(stat))
            except KeyError, e:
                logging.warning("No print config of {} (maybe no DEFAULT?)".format(stat))
            except Exception, e:
                raise e

    def printReport(self):
        """Get the string from the delegate and print it on a file"""
        self.config.file.write(self.getRawString())
        self.config.file.close()

    def print_general(self, config):
        logging.debug("Printing general stats")
        self.data["general"] = {"run": datetime.now(),
                                "from": self.config.fromDate,
                                "to": self.config.toDate,
                                "totalTweets": self.db.getTweetCount(self.config.fromDate,
                                                                       self.config.toDate)
                                }

    def print_clients(self, config):
        """Produces an output of clients with count"""
        logging.debug("Printing clients stats")
        minimum = config["minimum"]
        allData = self.db.getClientFrequencies(
                                    self.config.fromDate,
                                    self.config.toDate)

        over = [(data[0], data[1].decode("utf8")) for data in allData if data[0] >= minimum]
        below = [data[0] for data in allData if data[0] < minimum]
        countBelow = len(below)
        numBelow = reduce(__add__, below)
        others = (numBelow, '{} clients of {} or less'.format(countBelow, minimum - 1))

        self.data["clientCount"] = over + [others]

    def print_busiest(self, config):
        logging.debug("Printing busiest stats")
        number = config["number"]
        self.data["busiest"] = self.db.getTweetsPerUser(self.config.fromDate,
                                    self.config.toDate, number)

    def print_hashtags(self, config):
        logging.debug("Printing hashtags stats")
        number = config["number"]
        cloud = config["cloud"]
        data = self.db.getHashTags(self.config.fromDate, self.config.toDate)

        try:
            #step 2: remove stopwords
            with open(config["bannedtags"], 'r') as f:
                bannedtags = f.readlines()
            bannedtagset = set()
            for word in bannedtags:
                bannedtagset.add(word.lower().strip())
            logging.debug("Loaded {} stopwords".format(len(bannedtagset)))
        except Exception, e:
            logging.debug("Error processing bannedtags: {}".format(e))

        ##extract individual hashtags
        hashtags = {}

        # get a complete list of tags
        for twit in data:
            text = unidecode(str(twit[0]).decode("utf-8"))
            tags = [result for result in re.findall('(#[A-Za-z0-9]+)*', text) if len(result) > 0]
            for tag in tags:
                if tag.lower() not in bannedtagset:
                    if tag.lower() in hashtags:
                        hashtags[tag.lower()] += 1
                    else:
                        hashtags[tag.lower()] = 1

        sortedTags = sorted(hashtags.iteritems(), key=operator.itemgetter(1))[max(number, cloud) * -1:]
        cloudTags = sorted(sortedTags, key=lambda (a, b): a.lower().replace("#", ""))
        sortedTags.reverse()
        self.data["hashtags"] = sortedTags[0:number]
        self.data["cloudtags"] = cloudTags[0:cloud]
        logging.debug("{} of {} hashtags reported".format(len(self.data["hashtags"]), len(hashtags)))

    def print_words(self, config):
        logging.debug("Printing words stats")
        number = config["number"]
        cloud = config["cloud"]

        data = self.db.getTweets(self.config.fromDate, self.config.toDate)

        try:
            #step 2: remove stopwords
            with open(config["stopwords"], 'r') as f:
                logging.debug("Opening {}".format(f))
                stopwords = f.readlines()
            stopset = set()
            for word in stopwords:
                stopset.add(unidecode(word.lower().strip()))
            logging.debug("Loaded {} stopwords".format(len(stopset)))
        except Exception, e:
            logging.debug("Error processing stopwords: {}".format(e))

        ##extract individual hashtags
        words = {}

        # get a complete list of tags
        for twit in data:
            text = twit[0]
            #logging.debug(text)
            try:
                tags = [result for result in self.__split(text, stopwords)]
                for tag in tags:
                    if tag in words:
                        words[tag] += 1
                    else:
                        words[tag] = 1
            except Exception, e:
                logging.error("Error procesing: {}".format(twit[0]))
                raise e

        sortedWords = sorted(words.iteritems(), key=operator.itemgetter(1))[max(number, cloud) * -1:]
        cloudWords = sorted(sortedWords, key=lambda (a, b): a.lower().replace("#", ""))
        sortedWords.reverse()
        self.data["words"] = sortedWords[0:number]
        self.data["cloudwords"] = cloudWords[0:cloud]

    def __split(self, text, stopwords):
        """Function to tokenize a text removing unwanted texts"""
        ## TODO: borrar stopwords, enlaces, menciones, hashtags, puntuacion
        #Test to extract with \b[^\W\d_]+\b

        #step 1: unidecode and remove urls, users, hashtags and punctuation
        try:
            text = unidecode(str(text).decode("utf-8"))
            text = re.compile("[\w]+://[\w\.\/\d]+").sub(" ", text)
            text = re.compile("[\@\#][\w]+").sub(" ", text)
            text = re.compile(r'[\'\!\"\#\$\%\&\(\)\*\+\,\-\.\/\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\~\'\s]').sub(" ", text)
            text = re.compile(r'\b\w{1,5}\b').sub(" ", text)
            #step 2: remove stopwords
            words = []
            for word in text.split(" "):
                if len(word) > 0:
                    if not word.lower() in stopwords:
                        words.append(word)
            return words
        except UnicodeDecodeError:
            logging.warning("Pasando de {}".format(unidecode(text)))
            return []


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
            logging.debug(self.config.data["output"]["html"]["template"])
            templateFile = self.config.data["output"]["html"]["template"]
            with codecs.open(templateFile, 'r', 'utf-8') as f:
                template = env.from_string(f.read())
            logging.debug("Using {}".format(templateFile))
        except Exception, e:
            """If not found using a default"""
            logging.debug("Using default html template ({})".format(e))
            template = env.get_template("template.html")

        try:
            toPrint = template.render(data=self.data)
            return toPrint.encode('utf-8')
        except Exception, e:
            raise e
