import praw
import OAuth2Util
from imgurpython import ImgurClient
import time
import requests
import json
import os
import humanize
from .imgur_auth import *

def make_qr(repo):
    print(repo)
    repo = repo.rsplit('tag', 1)[0]
    repo = repo[18::]
    print(repo)
    req = requests.get("https://api.github.com/repos" + repo + "latest")
    data = json.loads(req.text)
    for item in data['assets']:
        if ".cia" in item['name']:
            url = item["browser_download_url"]
            file_size = item['size']
            file_size = humanize.naturalsize(file_size)
            upload = client.upload_from_url('https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl=' + url + '&choe=UTF-8')
            print(upload['link'])
            return upload['link'], file_size
        else:
            return None


r = praw.Reddit('3DS Homebrew QR Poster for /r/3DSHacks v0.2'
                'By /u/Im_Soul')
o = OAuth2Util.OAuth2Util(r)
# o.refresh()

client = ImgurClient(client_id, client_secret)

if not os.path.isfile("posts_scanned.txt"):
    posts_scanned = []

else:
    with open("posts_scanned.txt", "r") as f:
        posts_scanned = f.read()
        posts_scanned = posts_scanned.split("\n")
        posts_scanned = list(filter(None, posts_scanned))

subreddit = r.get_subreddit('test')

for submission in subreddit.get_new(limit=5):
    if submission.id not in posts_scanned:
        if 'github.com' in submission.url:
            link_to_release = submission.url
            if "release" in submission.url:
                finished = make_qr(link_to_release)
                if finished is not None:
                    comment = "QR (" + finished[1] + "): " + finished[0] + "\n ***** \n Made by /u/Im_Soul"
                    submission.add_comment(comment)
                    print("Replied to ", submission.id, " on ", time.asctime(time.localtime(time.time())))
                    posts_scanned.append(submission.id)


with open("posts_scanned.txt", "w") as f:
    for post_id in posts_scanned:
        f.write(post_id + "\n")
