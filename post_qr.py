import praw
import OAuth2Util
from imgurpython import ImgurClient
import time
import requests
import json
import os
import humanize
from .imgur_auth import *

# sweet mother of imports

def make_qr(repo):
    """
    Takes a github url, uses the github api to get the direct download url and size, and uses google api to make a qr.
    It returns the link to the qr (not on imgur) and the formatted file size
    """
    if 'tag' in repo:
        repo = repo.rsplit('tag', 1)[0]                         # cut the url up to /tag/
        repo = repo[18::]                                       # cut out www.~~~ blah up to /user/repo
    else:
        repo = repo.rsplit('releases', 1)[0]                         # cut the url up to /tag/
        repo = repo[18::]
    req = requests.get("https://api.github.com/repos" + repo + "latest")        # change to proper api format
    data = json.loads(req.text)
    for item in data['assets']:
        if ".cia" in item['name']:                          # if the download links have cia, make qr, else return None
            url = item["browser_download_url"]              # search for keys containing url and size
            file_size = item['size']
            file_size = humanize.naturalsize(file_size)
            upload = client.upload_from_url(                # google chart api to make qr
                'https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl=' + url + '&choe=UTF-8')
            return upload['link'], file_size
        else:
            return None


r = praw.Reddit('3DS Homebrew QR Poster for /r/3DSHacks v0.2'
                'By /u/Im_Soul')

o = OAuth2Util.OAuth2Util(r)        # create reddit oauth
# o.refresh()

client = ImgurClient(client_id, client_secret)      # imgur app credentials (from imgur_auth.py)

if not os.path.isfile("posts_scanned.txt"):         # check for posts_scanned.txt, if not, make empty list to store ids
    posts_scanned = []                              # if so, import the ids stored to the file

else:
    with open("posts_scanned.txt", "r") as f:
        posts_scanned = f.read()
        posts_scanned = posts_scanned.split("\n")
        posts_scanned = list(filter(None, posts_scanned))

subreddit = r.get_subreddit('3dshacks')            # subreddit to scan

for submission in subreddit.get_new(limit=5):       # get 5 posts
    if submission.id not in posts_scanned:          # check if we already checked the id
        if 'github.com' in submission.url:          # check if url is github
            link_to_release = submission.url
            if "release" in submission.url:             # check if it's a release (bad way of doing it)
                finished = make_qr(link_to_release)
                if finished is not None:                # if 'make_qr()' was a success
                    comment = "QR (" + finished[1] + "): " + finished[0] + "\n ***** \n Made by /u/Im_Soul"  # comment formatting
                    submission.add_comment(comment)
                    print("Replied to ", submission.id, " on ", time.asctime(time.localtime(time.time())))   # run log
                    posts_scanned.append(submission.id)     # add id to list


with open("posts_scanned.txt", "w") as f:               # write from the list to the file
    for post_id in posts_scanned:
        f.write(post_id + "\n")
