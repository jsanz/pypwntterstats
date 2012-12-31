import argparse
from datetime import date, timedelta


def fromDateToInt(aDate):
    """Creates a date from YYMMDD format"""
    return '{:%Y%m%d}'.format(aDate)


def fromIntToDate(iDate):
    """Creates a YYMMDD string from a Date"""
    year = int(str(iDate)[0:4])
    month = int(str(iDate)[4:6])
    day = int(str(iDate)[6:8])
    return date(year, month, day)


def formattedDate(string):
    """Defines a argparse type format for YYYYMMDD string daes"""
    try:
        return fromIntToDate(string)
    except Exception:
        raise argparse.ArgumentTypeError(
                    "Error parsing date {}".format(string))


def yesterdayFormatted():
    """Default for FROM parameter, 0:0 of yesterday"""
    return fromDateToInt(date.today() + timedelta(days=-1))


def todayFormatted():
    """Defaul for TO parameter, 23:59:59 of yesterday"""
    return fromDateToInt(date.today() + timedelta(days=-1))


class Arguments():

    def __init__(self, customArgs=None):
        parser = argparse.ArgumentParser(
            description='Process pwntter database to generate fancy reports',
            epilog="Jorge Sanz (c)2012 - @xurxosanz - http://jorgesanz.net")

        parser.add_argument("-q", "--quiet", action="store_true")

        parser.add_argument("-t", "--title", action="store_true")

        parser.add_argument("-c", "--config", type=file, required=True,
                            help="Configuration file in YML format")

        parser.add_argument("-f", "--format", choices=["json", "html"],
                            required=True, help="Format for the output file")

        parser.add_argument("-o", "--output", type=argparse.FileType('w'),
                            required=True, help="Output file name")

        parser.add_argument("-F", "--FROM", type=formattedDate,
                            default=yesterdayFormatted(),
                            help="Define the starting day to retrieve the "
                                    "report in YYYYMMDD format. Defaults to 00:00 "
                                    "of yeserday.")

        parser.add_argument("-T", "--TO", type=formattedDate,
                            default=todayFormatted(),
                            help="Define the last day to retrieve the "
                                 "report in YYYYMMDD format. Defaluts to 23:59:59 "
                                 "of yesterday")

        parser.add_argument("-u", "--user", action="store", required=True,
                            help="User to query the database")

        if customArgs:
            self.args = parser.parse_args(customArgs)
        else:
            self.args = parser.parse_args()
