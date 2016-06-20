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

    val = struct.unpack('!Q', req.content)
    titleid = "0x%0.16X" % val[0]

    req = requests.get(url, headers={'Range': 'bytes='+str(int(rawsize)-12984)+"-"+str(int(rawsize)-12984+511)})
    shortdesc = req.text[0:128].translate({ord(c): None for c in '\x00'})    # strip
    longdesc = req.text[128:384].translate({ord(c): None for c in '\x00'})   # the
    publisher = req.text[384:512].translate({ord(c): None for c in '\x00'})  # nulls!

    req.close()
    return titleid, shortdesc, longdesc, publisher


def determine_api_url(original_url):
    """
    Convert our original reddit URL into a corresponding github API url for the release.
    """
    upr_string = original_url.split('github.com/', 1)[1]
    upr_tokens = upr_string.split('/')

    if upr_tokens[0] and upr_tokens[1]:             # make sure we have a user and a project at least
        if len(upr_tokens) >= 5 and upr_tokens[4] is not '':
            return "https://api.github.com/repos/" + upr_tokens[0] + "/" + upr_tokens[1] + "/releases/tags/" + upr_tokens[4]
        return "https://api.github.com/repos/" + upr_tokens[0] + "/" + upr_tokens[1] + "/releases/latest"
    return


def make_qr(github_api_url, headers, auth):
    """
    Takes a github api URL to get the direct download url and size, and uses google api to make a qr.
    It returns a list of tuples containing the link to the qr, file name, and the formatted file size, as well as the titleID,
    short description, long description, and publisher fields from the SMDH data.
    """
    retlist = []    # define a blank list to return
    req = requests.get(github_api_url, headers=headers, auth=auth)
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
                if ciainfo[0][0:6] == "0x0004":                 # only add to the list if this is a 3DS cia
                    retlist.append((qr_url, item_name, file_size, ciainfo[0], ciainfo[1], ciainfo[2], ciainfo[3]))

    req.close()
    return retlist

def main():

    r = praw.Reddit('3DS Homebrew QR Poster for /r/3DSHacks v1.0'
                    'By /u/Im_Soul')

    o = OAuth2Util.OAuth2Util(r)        # create reddit oauth
    # o.refresh()

    gc = open('github_credentials.txt')
    auth = [i for i in gc]
    ghauth = (auth[0].rstrip('\n'), auth[1].rstrip('\n'))

    headers = {
        'User-Agent': '3DS-QR-Bot',
    }

    if not os.path.isfile("posts_scanned.txt"):         # check for posts_scanned.txt, if not, make empty list to store ids
        posts_scanned = []                              # if so, import the ids stored to the file

    else:
        with open("posts_scanned.txt", "r") as f:
            posts_scanned = f.read()
            posts_scanned = posts_scanned.split("\n")
            posts_scanned = list(filter(None, posts_scanned))

    if not os.path.isfile("run_log.txt"):               # check for run_log.txt, if not, make empty list to store ids
        run_log = []                                    # if so, import the ids stored to the file

    else:
        with open("run_log.txt", "r") as l:
            run_log = l.read()
            run_log = run_log.split("\n")
            run_log = list(filter(None, run_log))

    subreddit = r.get_subreddit('3dshacks')                 # subreddit to scan

    for submission in subreddit.get_new(limit=5):       # get 5 posts
        if submission.id not in posts_scanned:          # check if we already checked the id
            if 'github.com' in submission.url:          # check if url is github
                comment = ''                            # blank out our comments
                api_url = determine_api_url(submission.url)
                if api_url:
                    qrlist = make_qr(api_url, headers, ghauth)
                if qrlist:                  # if 'make_qr()' was a success
                    for qrentry in qrlist:
                        comment = comment +\
                                  'QR Code for ['+ qrentry[1] + ' (' + qrentry[2] + ')](' + qrentry[0] + ')  \n' +\
                                  '\n' +\
                                  '* Title ID: ' + qrentry[3] + '  \n' +\
                                  '* Short Description: ' + qrentry[4] + '  \n' +\
                                  '* Long Description: ' + qrentry[5] + '  \n' +\
                                  '* Publisher: ' + qrentry[6] + '  \n' +\
                                  '\n' +\
                                  '*****\n'
                    if comment is not '':               # check if we have anything to post
                        comment += '*[3DS QR Bot](https://github.com/thesouldemon/3DS-QR-Poster)'
                        submission.add_comment(comment)
                        print(comment)
                        log = "Replied to " + submission.id + " on " + time.asctime(time.localtime(time.time()))
                        run_log.append(log)                     # log post id and time a post was replied to
                        posts_scanned.append(submission.id)     # add id to list

    with open("posts_scanned.txt", "w") as f:               # write from posts_scanned list to the file
        for post_id in posts_scanned:
            f.write(post_id + "\n")

    with open("run_log.txt", "w") as l:                     # write from the run_log to the file
        for log_entry in run_log:
            l.write(log_entry + "\n")

if __name__ == '__main__':
    main()
