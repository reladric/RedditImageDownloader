from configparser import ConfigParser
from model.database import Downloads,DBParams,SubscribedSubReddits
from getter.getem import PathHolder
class ConfigReader:
    def __init__(self):
        self.cfparser=ConfigParser()
    def readParam(self,file,wrapper):
        self.cfparser.read(file)
        if (isinstance(wrapper,DBParams)):
            wrapper.database=self.cfparser["Database"]["database"]
            wrapper.user=self.cfparser["Database"]["user"]
            wrapper.password=self.cfparser["Database"]["password"]
            wrapper.driver="mysql+mysqlconnector"
            wrapper.hostname=self.cfparser["Database"]["host"]
            wrapper.port=self.cfparser["Database"]["port"]
        elif(isinstance(wrapper,SubscribedSubReddits)):
            readReddits=self.cfparser["Subreddit"]["list"]
            wrapper.subreddits=set()
            subreddits=readReddits.split(",")
            for subreddit in subreddits:
                wrapper.subreddits.add(Downloads(subredditName=subreddit))
        elif(isinstance(wrapper,PathHolder)):
            wrapper.pathToHold=self.cfparser["Download"]["folder"]
        return wrapper
