from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
import threading
import logging
import os
import requests
import string
from model.database import ErrorLog
class Getter(threading.Thread):
    def __init__(self,dwQ,errQ,stopped,filePath,initFile,cfreader):
        threading.Thread.__init__(self,daemon=False)
        self.errorQueue=errQ
        self.downloadQueue=dwQ
        self.stopped=stopped
        self.imgurClient=ImgurClient("4ff2bb9d9c640f2", "8b036ffa680a1304814f48eff9e93206c096727f")
        self.paramReader=cfreader
        self.downloadPath=PathHolder()
        self.downloadPath = self.paramReader.readParam(filePath+ "\\" + initFile,self.downloadPath)
        logger = logging.getLogger('Image_Downloader')
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('logs/downloads.log')
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
        logger.debug("-----------------------------")
        logger.debug("Init complete")

    def run(self):
        logger= logging.getLogger('Image_Downloader')
        logger.debug("Thread started")
        while not self.stopped.is_set():
            self.getURL()

    def getURL(self):
        logger= logging.getLogger('Image_Downloader')            
        while not self.downloadQueue.empty():
            downloadList=None
            try:
                downloadList=self.downloadQueue.get()
            except:
                continue
            self.downloadQueue.task_done()
            logger.debug("Dequeued and marked done")    
            for downloadObject in downloadList:
                if "imgur" in downloadObject.domain:
                    logger.debug("Imgur URL found")
                    fileName, fileExtension = os.path.splitext(downloadObject.url)
                    if "/a/" in fileName:
                        albumPart=downloadObject.url.split("/a/")[1]
                        albumName=albumPart.split('/')[0].split('#')[0]
                        self.handleAlbum(albumName,downloadObject.subreddit,downloadObject.id,downloadObject.title)
                    elif fileExtension is not None and len(fileExtension) > 0:
                        self.handleImage(downloadObject.url,downloadObject.subreddit,downloadObject.id,downloadObject.title,fileExtension)
                    else:
                        fileId=downloadObject.url.split("/")[-1]
                        for f in fileId.split(","):
                            self.handleURL(f,downloadObject.subreddit,downloadObject.id,downloadObject.title)
                else:
                    logger.debug("Non imgur URL")
                    self.errorQueue.put(ErrorLog(subredditName=downloadObject.subreddit,failedItemName=downloadObject.id,failReason="Domain not suppported"))
        logger.debug("Returning from fuction")
            
                        
                
    def handleImage(self,url,redditName,id,title,fileExtension):
        logger= logging.getLogger('Image_Downloader')
        directory=self.downloadPath.pathToHold + redditName
        valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
        name=''.join(c for c in title if c in valid_chars)
        fname = (name[:30]) if len(name) > 30 else name
        fileExtension=fileExtension.split("?")[0]
        file=directory + "\\" + fname +"_" + id +  fileExtension
        logger.debug("From "+ url + "to " + file)
        try:
            if not os.path.exists(directory):
                os.mkdir(directory)
        except OSError as e:
            logger.debug(e.strerror)
            self.errorQueue.put(ErrorLog(subredditName=redditName,failedItemName=id,failReason=e.strerror,retries=0))
        if not os.path.exists(file) and not os.path.exists(directory + "\\" + name +"_" + id +  fileExtension):
            try:
                r = requests.get(url, stream=True)
                if r.status_code == 200:
                    with open(file, 'wb') as f:
                        for chunk in r.iter_content(1024):
                            f.write(chunk)
            except (requests.exceptions.RequestException,requests.exceptions.ConnectionError,requests.exceptions.HTTPError,requests.exceptions.URLRequired,requests.exceptions.TooManyRedirects,requests.exceptions.ConnectTimeout,requests.exceptions.ReadTimeout,requests.exceptions.Timeout) as e:
                logger.debug(e.__class__.__name__)
                self.errorQueue.put(ErrorLog(subredditName=redditName,failedItemName=id,failReason=e.__class__.__name__,retries=0))
            except OSError as e:
                logger.debug(e.strerror +" " + file )
                self.errorQueue.put(ErrorLog(subredditName=redditName,failedItemName=id,failReason=e.strerror,retries=0))
        
    def handleAlbum(self,albumName,redditName,id,title):
        logger= logging.getLogger('Image_Downloader')
        logger.debug("Found an Album to download" + albumName)
        for imageObject in self.imgurClient.get_album_images(albumName):
            logger.debug("Next item in the album")
            self.handleImageObject(imageObject,redditName,title)
     
    def handleURL(self,fileId,subreddit,id,title):
        logger= logging.getLogger('Image_Downloader')
        logger.debug("Found a wrapped image: "+ fileId)
        try:
            image=self.imgurClient.get_image(fileId)
            logger.debug("Got the image back " )
            self.handleImageObject(image,subreddit,title)
            logger.debug("Done with this wrap")
        except ImgurClientError as e:
            logger.debug(e.error_message)
            logger.debug(e.status_code)
        except Exception as e:
            logger.debug(type(e))

        
    def handleImageObject(self,imageObject,reddit,title):
        logger= logging.getLogger('Image_Downloader')
        logger.debug("Got the an image to download " )            
        fileName, fileExtension = os.path.splitext(imageObject.link)
        if fileExtension is not None and len(fileExtension) > 0:
            self.handleImage(imageObject.link,reddit,imageObject.id,title,fileExtension)
        
class PathHolder:
    def __init__(self):
        self.pathToHold=None