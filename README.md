# rdownloader
Downloads Images linked in any subreddtt to a local location

* Currently supports only imgur
* Respects the reddits API rules. (Might be 'err'ing on the side of safety)
* Uses MySQL to 
* Loads the subreddits to scan from a ini file

Suggestions regarding best practices as well as ideas are more than welcome
# Instructions
* Edit the "info.ini" file with mysql db details, subreddits to download images from (comma separated list) and path where downloads need to be saved. 
* logs folder will have multiple debug level logs. Delete them often since they grow crazy fast
