from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String,text
from sqlalchemy.types import TIMESTAMP
from sqlalchemy import text

global Base
Base=declarative_base()
class Downloads(Base):
    __tablename__='downloads'
    subredditName=Column(String(100), primary_key=True)
    totalDownloads=Column(Integer)
    newFinderKey=Column(String(30))
    oldFinderKey=Column(String(30))
    latestDate=Column(TIMESTAMP)

class ErrorLog(Base):
    __tablename__='errorLog'
    subredditName=Column(String(100),primary_key=True)
    failedItemName=Column(String(100),primary_key=True)
    failReason=Column(String(100))
    retries=Column(Integer)
    failTime=Column(TIMESTAMP)
    