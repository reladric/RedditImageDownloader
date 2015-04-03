import os
import pdb
from switcher.switchem import Switcher
global __basepath,__initFile
__initFile="info.ini"
__basepath = os.path.dirname(os.path.abspath(__file__))
sw=Switcher(__basepath,__initFile)
sw.load_all_subreddits()
sw.start_work()