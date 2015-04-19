# RedditImageDownloader
Downloads Images linked in any subreddtt to a local location
Run at a regular interval to keep getting the newer images in any selected subreddit 
* Currently supports only imgur
* Respects the reddit's API rules. (Might be 'err'ing on the side of safety)
* Uses ~~MySQL~~ sqlite to 'bookmark' posts until which download is completed
* Loads the subreddits to scan from a ini file
# Requirements
* Developed for Python 3.4.x+
* Following modules are used :
    ** os
    ** threading
    ** logging
    ** time
    ** queue
    ** datetime`
    ** configparser
    ** sqlalchemy (http://www.sqlalchemy.org/) (need to be installed)
    ** requests (http://docs.python-requests.org/en/latest/) (need to be installed)
    ** imgurpython (https://github.com/Imgur/imgurpython) (need to be installed)
    ** pysqlite (need to be installed)

# Instructions
* Edit the "info.ini" file with sqlite db file name (database), subreddits to download images from (comma separated list) and path where downloads need to be saved.
* logs folder will have multiple debug level logs. Delete them often since they grow crazy fast
* Run using command "python main.py" from base folder
Suggestions regarding best practices as well as ideas are more than welcome