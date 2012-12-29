import argparse
from datetime import date, timedelta


def fromDateToInt(aDate):
    return '{:%Y%m%d}'.format(aDate)


def fromIntToDate(iDate):
    year = int(str(iDate)[0:4])
    month = int(str(iDate)[4:6])
    day = int(str(iDate)[6:8])
    return date(year, month, day)


def formattedDate(string):
    try:
        return fromIntToDate(string)
    except Exception:
        raise argparse.ArgumentTypeError(
                    "Error parsing date {}".format(string))


def yesterdayFormatted():
    return fromDateToInt(date.today() + timedelta(days=-1))


def todayFormatted():
    return fromDateToInt(date.today())


class Arguments():

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Process pwntter database to generate fancy reports',
            epilog="Jorge Sanz (c)2012 - @xurxosanz - http://jorgesanz.net")

        parser.add_argument("-q", "--quiet", action="store_true")

        parser.add_argument("-c", "--config", type=file, required=True,
                            help="Configuration file in YML format")

        parser.add_argument("-f", "--format", choices=["json", "html"],
                            required=True, help="Format for the output file")

        parser.add_argument("-o", "--output", type=argparse.FileType('w'),
                            required=True, help="Output file name")

        parser.add_argument("-F", "--FROM", type=formattedDate,
                            default=yesterdayFormatted(),
                            help="Define the starting day to retrieve the "
                                    "report in YYYYMMDD format.")

        parser.add_argument("-T", "--TO", type=formattedDate,
                            default=todayFormatted(),
                            help="Define the last day to retrieve the "
                                 "report in YYYYMMDD format.")

        parser.add_argument("-u", "--user", action="store", required=True,
                            help="User to query the database")

        self.args = parser.parse_args()
