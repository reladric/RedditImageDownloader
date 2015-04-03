from model.database import DBSpeaker,SubscribedSubReddits
from hitter.hitem import Hitter
from getter.getem import Getter
from redutil.readem import ConfigReader
import threading
import queue
import logging
class Switcher:
    def __init__(self,__basepath,__initFile):
        logger = logging.getLogger('controller')
        logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
        fh = logging.FileHandler('logs/controller.log')
        fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
        formatter = logging.Formatter('[%(filename)s:%(lineno)s - %(funcName)20s() ] %(asctime)s %(levelname)s:%(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
# add the handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)
        logger.debug("------------------------")
        self.cfreader=ConfigReader()
        self.basepath=__basepath
        self.initFile=__initFile
        self.db = DBSpeaker(__basepath,__initFile,self.cfreader)
        if self.db.status==1:
            self.db.connect_db()
        if self.db.status==2:
            self.db.setup_database()
        self.stopFlag=threading.Event()
        self.hitter=Hitter(self.stopFlag)
        self.hitter.start()
        self.downloadQueue=queue.Queue()
        self.errorQueue=queue.Queue()
        self.getter=Getter(self.downloadQueue,self.errorQueue,self.stopFlag,__basepath,__initFile,self.cfreader)
        self.getter.start()

    def start_work(self):
        logger = logging.getLogger('controller')
        logger.debug("Starting work")
        subreddits=self.db.read_all_downloads()
        logger.debug("All downloads read")
        for subreddit in subreddits:
            logger.debug("Starting for "  + subreddit.subredditName)
            if subreddit.totalDownloads is None:
                logger.debug("Setting download count to 0")
                subreddit.totalDownloads=0
            queuedCount=0
            logger.debug("About to get later posts") 
            while True:
                logger.debug("API call")
                responseContent=self.hitter.hitFor(subreddit.subredditName,subreddit.newFinderKey,0)
                if responseContent is None:
                    break
                logger.debug("Queueing the response")
                self.downloadQueue.put(responseContent.data)
                queuedCount+=len(responseContent.data)
                if responseContent.before is None:
                    if len(responseContent.data) >0:
                        logger.debug("No more later posts. Setting the mark")
                        subreddit.newFinderKey="t3_"+responseContent.data[0].id
                        if subreddit.oldFinderKey is None:
                            subreddit.oldFinderKey = "t3_"+responseContent.data[-1].id
                    else:
                        logger.debug("Found nothing. Not updating before mark")
                    break
                else:
                    logger.debug("Setting the mark.")
                    subreddit.newFinderKey=responseContent.before
            logger.debug("Waiting for downloads to complete")
            self.downloadQueue.join()
            subreddit.totalDownloads+=queuedCount-self.errorQueue.qsize()
            while not self.errorQueue.empty():
                try:
                    self.db.write_row(self.errorQueue.get())
                except:
                    continue
                self.errorQueue.task_done()
            self.db.write_row(subreddit)
            queuedCount=0
            responseContent=None
            logger.debug("About to get older posts")     
            while True:
                logger.debug("API call")
                responseContent=self.hitter.hitFor(subreddit.subredditName,subreddit.oldFinderKey,1)
                if responseContent is None:
                    break
                logger.debug("Queuing the response")
                self.downloadQueue.put(responseContent.data)
                queuedCount+=len(responseContent.data)
                if responseContent.after is None:
                    if len(responseContent.data) >0:
                        logger.debug("No more later posts. Setting the mark")
                        subreddit.oldFinderKey="t3_"+responseContent.data[-1].id
                    else:
                        logger.debug("Found nothing. Not updating before mark")
                    break
                else:
                    logger.debug("Setting the mark.")
                    subreddit.oldFinderKey=responseContent.after
            logger.debug("Waiting for downloads to complete")
            self.downloadQueue.join()
            subreddit.totalDownloads+=queuedCount-self.errorQueue.qsize()
            while not self.errorQueue.empty():
                try:
                    self.db.write_row(self.errorQueue.get())
                except:
                    continue
                self.errorQueue.task_done()
            self.db.write_row(subreddit)
        logger.debug("Complete")
        self.stopFlag.set()
                    
    def load_all_subreddits(self):
        tosubreddits=SubscribedSubReddits()
        tosubreddits=self.cfreader.readParam(self.basepath+"\\"+self.initFile,tosubreddits)
        exsubreddits=SubscribedSubReddits()
        exsubreddits.subreddits=self.db.read_all_downloads()
        print ("About to load subreddits")
        for exsub in exsubreddits.subreddits:
            print ("Validating existing subreddits")
            existFlag=0
            for tosub in tosubreddits.subreddits:
                if tosub.subredditName == exsub.subredditName:
                    existFlag=1
                    break
            if existFlag == 0:
                self.db.delete_row(exsub)
        for tosub in tosubreddits.subreddits:
            print("Loading new subreddits")
            existFlag=0
            for exsub in exsubreddits.subreddits:
                if tosub.subredditName == exsub.subredditName:
                    existFlag=1
                    break
            if existFlag == 0:
                self.db.write_row(tosub)
