from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import desc

Base = declarative_base()


class User(Base):
    """Map the users table"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    screen_name = Column(String)
    name = Column(String)
    protected = Column(Integer)

    tweets = relationship("Tweet",
                primaryjoin="User.id==Tweet.user_id",
                backref="user")

    def __repr__(self):
        return "@{}: {} {}".format(self.screen_name, self.name,
            "(protected)" if self.protected else "")


class Tweet(Base):
    """Map the tweets table"""
    __tablename__ = 'tweets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    screen_name = Column(String)
    text = Column(String)
    created_at = Column(DateTime)
    source = Column(String)

    def __repr__(self):
        return "@{}: {} ({})".format(self.screen_name, self.text, self.created_at)


class Database():
    """Queries the database to gather all the data"""

    def __init__(self, config):
        """Connects to the database

            config: db section of the configuration"""

        engine = self.__my_create_engine(config)

        if not engine:
            raise Exception("No engine created")

        engine.connect()
        #metadata = MetaData(bind=engine)
        Session = sessionmaker(bind=engine)

        # Set the objects to work with
        self.session = Session()

    def getTweetCount(self, fromDate, toDate):
        """Return the amount of tweets posted on that date"""
        return self.session.query(func.count(Tweet.id)).\
                filter(Tweet.created_at > fromDate).\
                filter(Tweet.created_at < toDate).scalar()

    def getClientFrequencies(self, fromDate, toDate):
        """Return a list of tuples with the count and twitter clients

            fromDate: formatted from date as 'YYY-MM-DD HH:MM:SS'
            toDate:last formatted to date as 'YYY-MM-DD HH:MM:SS'"""
        return self.session.query(func.count(Tweet.source), Tweet.source).\
                group_by(Tweet.source).\
                order_by(desc(func.count(Tweet.source))).\
                filter(Tweet.created_at > fromDate).\
                filter(Tweet.created_at < toDate).all()

    def getTweetsPerUser(self, fromDate, toDate):
        """Returns a list of users and the number of tweets written. It hides
            users that have their accounts protected.

            fromDate: formatted from date as 'YYY-MM-DD HH:MM:SS'
            toDate:last formatted to date as 'YYY-MM-DD HH:MM:SS'"""
        #print self.session.query(self.tweets).filter_by(screen_name='xurxosanz').first()
        for user in self.session.query(User).join(Tweet).\
            filter(User.protected == 1):
            print user
        pass

    def __my_create_engine(self, config):
        """Creates a SQLAlchemy engine depending on the
           configuration passed. At this time it only supports
           mysql"

           config: db section of the config file"""
        return {
            'mysql': lambda c: create_engine(
                                "mysql://" + c["user"] + ":" + c["password"] +
                                "@" + c["host"] + "/" + c["database"],
                                isolation_level="READ UNCOMMITTED")
        }[config["type"]](config)
