class SubRedditResponseData:
    def __init__(self,id,url,domain,subreddit,title):
        self.id=id
        self.url=url
        self.domain=domain
        self.subreddit=subreddit
        self.title=title
class SubRedditResponseChildren:
    def __init__(self,after,before,data):
        self.data=data
        self.after=after
        self.before=before