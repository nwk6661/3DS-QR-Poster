#!/usr/bin/python3

import praw
import OAuth2Util
import time
import requests
import json
import os
import humanize
import struct

# sweet mother of imports

def get_cia_info(url):
    """
    Takes a CIA url, and collects the titleID as well as the SMDH title/creator text in english.
    It returns titleid, shortdesc, longdesc, publisher
    """
    req = requests.get(url, headers={'Range': 'bytes=11292-11299'})
    rawsize = req.headers['Content-Range'].split('/')[1]

    val = struct.unpack('!Q', bytes(req.text, 'latin1'))
    titleid = hex(val[0])

    req = requests.get(url, headers={'Range': 'bytes='+str(int(rawsize)-12984)+"-"+str(int(rawsize)-12984+511)})
    shortdesc = req.text[0:128]
    longdesc = req.text[128:384]
    publisher = req.text[384:512]

    return titleid, shortdesc, longdesc, publisher

def make_qr(repo):
    """
    Takes a github url, uses the github api to get the direct download url and size, and uses google api to make a qr.
    It returns the link to the qr (not on imgur) and the formatted file size, as well as the titleID, short description,
    long description, and publisher fields from the SMDH data.
    """

    repo = repo.rsplit('releases', 1)[0]                         # cut the url up to /releases/
    repo = repo[18::]
    req = requests.get("https://api.github.com/repos" + repo + "releases/latest")        # change to proper api format
    data = json.loads(req.text)

    if 'assets' in data:
        for item in data['assets']:
            item_name = item['name']
            if (item_name[(len(item_name)-3)::]) == "cia":      # if the download links have cia, make qr, else return None
                url = item["browser_download_url"]              # search for keys containing url and size
                ciainfo = get_cia_info(url)

                file_size = item['size']
                file_size = humanize.naturalsize(file_size)
                qr_url = ('https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl=' + url + '&choe=UTF-8.png')
                return qr_url, file_size, ciainfo[0], ciainfo[1], ciainfo[2], ciainfo[3]
        return None


def main():
    # get_cia_info("https://github.com/Cruel/freeShop/releases/download/1.2/freeShop-1.2.cia")
    # return None


    r = praw.Reddit('3DS Homebrew QR Poster for /r/3DSHacks v0.5'
                    'By /u/Im_Soul')

    o = OAuth2Util.OAuth2Util(r)        # create reddit oauth
    # o.refresh()


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
                        comment = '[QR Code (' + finished[1] + ')](' + finished[0] + ')' +\
                                  '\n ***** \n' + finished[2] +'\n'+ finished[3] +'\n'+ finished[4] +'\n'+ finished[5] +\
                                  '\n ***** \n Made by /u/Im_Soul'  # comment formatting
                        submission.add_comment(comment)
                        print(comment)
                        print("Replied to ", submission.id, " on ", time.asctime(time.localtime(time.time())))   # run log
                        posts_scanned.append(submission.id)     # add id to list


    with open("posts_scanned.txt", "w") as f:               # write from the list to the file
        for post_id in posts_scanned:
            f.write(post_id + "\n")

if __name__ == '__main__':
    main()
