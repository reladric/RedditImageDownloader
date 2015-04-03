from hitter.redurllib import RedditURL
from reddit.SubReddit  import SubRedditResponseChildren,SubRedditResponseData
import time
import requests
#from threading import Thread,Lock,Condition
import threading
import logging
from requests import Request, Session
class Hitter(threading.Thread):
    def __init__(self,event):
        logger = logging.getLogger('Reddit_API_Hitter')
        logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh = logging.FileHandler('logs/reddit_api.log')
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
        logger.debug("-------------------------------")
        threading.Thread.__init__(self,daemon=False)
        self.stopped=event
        self.urllist=RedditURL()
        self.requestLeft=30
        self.limit=25
        self.connectSession=requests.Session()
        self.connectSession.headers.update({'User-Agent':'python3_4/win8_64:RedditDownloader:v0.1b(by /u/reladric)'})
        self.lock= threading.Lock()
        self.conditionObj=threading.Condition(self.lock)
         
    def run(self):
        logger = logging.getLogger('Reddit_API_Hitter')
        while not self.stopped.wait(60):
            logger.debug("Resetting max hits")
            self.resetCounter()

    def resetCounter(self):
        self.conditionObj.acquire()
        self.requestLeft=30
        self.conditionObj.notifyAll()
        self.conditionObj.release()
            
    def hitFor(self,subreddit,where,forwardFlag):
        logger = logging.getLogger('Reddit_API_Hitter')        
        logger.debug("New hit")
        urlToHit=self.urllist.baseURL+self.urllist.URLtypes["subreddit"]+subreddit+"/new.json"
        payload={'limit':self.limit}
        if forwardFlag == 0:
            payload['before']=where
        else:
            payload['after']=where
        self.conditionObj.acquire()
        if self.requestLeft == 0:
            logger.debug("Hit cap. Waiting for reset")
            self.conditionObj.wait()
        returnObj=None
        try:
            req = Request('GET',  urlToHit,
                          params=payload
                      )
            prepped = self.connectSession.prepare_request(req)
            logger.debug("Hitting the url" + req.url)
            r=self.connectSession.send(prepped)
            response=r.json()
            dataObj=[]
            for data in response["data"]["children"]:
                dataObj.append(SubRedditResponseData(data["data"]["id"],data["data"]["url"],data["data"]["domain"],data["data"]["subreddit"],data["data"]["title"]))
            returnObj=SubRedditResponseChildren(response["data"]["after"],response["data"]["before"],dataObj)
            self.requestLeft=self.requestLeft - 1
        except Exception as e:
            logger.debug(type(e))
        finally:
            self.conditionObj.release()
        return returnObj