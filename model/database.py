from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import DatabaseError
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser
import model.tables
import logging
from model.tables import Downloads,ErrorLog

class DBSpeaker:
    def __init__(self, basepath,initFile,cfreader):
        self.baspath=basepath
        self.status=0
        self.engine=None
        self.url=None
        self.dbparam=DBParams()
        self.cfreader=cfreader
        self.dbparam=cfreader.readParam(basepath+"\\"+initFile,self.dbparam)
        self.status=1


    def read_db_settings(self, basepath,initFile):
        configreader=ConfigParser()
    
    def setup_database(self):
        try :
            #self.engine.execute("CREATE DATABASE IF NOT EXISTS "+ self.dbparam.database)
            self.status=3
        except DatabaseError as e:
            messageString=e.orig
            messageString=format(messageString)
            messageList=messageString.split(':',1)
            if messageList[0] == "1007":
                self.status=3
            else:
                self.status=-3
                return self.status
    #self.url=URL(self.dbparam.driver,self.dbparam.database+".db")
        try:
            self.engine=create_engine(self.url)
        except DatabaseError as e:
            self.status=-4
            return self.status
        self.status=4
        try:
            model.tables.Base.metadata.create_all(self.engine)
        except DatabaseError as e:
            self.status=-5
            return self.status
        self.status=5
        self.sessionHolder=sessionmaker(bind=self.engine)
        self.session=self.sessionHolder()
        return self.status
        
    def connect_db(self):

        self.url=URL(self.dbparam.driver,database=self.dbparam.database)
        try:
            self.engine = create_engine(self.url)
        except Exception as e:
            self.status=-2
        self.status=2
        
    def write_row(self, object):
        logger = logging.getLogger('controller')
        logger.debug("Writing Someone")
        try:
            self.session.add(object)
            self.session.commit()
        except InvalidRequestError as e:
            logger.debug(e)
            return False
        return True

    def delete_row(self,object):
        logger = logging.getLogger('controller')
        logger.debug("Deleting someone")
        try:
            self.session.delete(object)
            self.session.commit()            
        except InvalidRequestError as e:
            logger.debug(e)
            return False
        return True

    def read_all_downloads(self):
        query=self.session.query(Downloads)
        self.session.add_all(query.all())
        return set(query.all())
        
    def __exit__(self):
        self.session.close()

class DBParams:
    def __init__(self):
        self.driver=None
        self.host=None
        self.port=None
        self.user=None
        self.password=None
        self.database=None
class SubscribedSubReddits:
    def __init__(self):
        self.subreddits=None