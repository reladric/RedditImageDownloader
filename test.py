import sys
filepath = "C:\\Users\\Sarvo\\Code\\RedditDownloader\\main.py"
global_namespace = {
    "__file__": filepath,
    "__name__": "__main__",
    }
exec(compile(open(filepath,"rb").read(),"C:\\Users\\Sarvo\\Code\\RedditDownloader\\main.py",'exec'), global_namespace )
sys.exit(0)