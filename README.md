# 3DS-QR-Poster

A python bot that creates and posts QR codes to reddit for new 3DS hombrebrew posted on the /r/3DShacks subreddit.

    pip install praw
    pip install praw-oauth2util
    pip install imgurpython
    pip install humanize
    
You will need to [set up oauth2util](https://github.com/SmBe19/praw-OAuth2Util/blob/master/OAuth2Util/README.md) and create a file called `posts_scanned.txt`

You may also have a file called `imgur_auth.py` with variables `client_id` and `client_secret`, or you may leave them in the main `post_qr.py`

You will also need to [register an imgur application](https://api.imgur.com/oauth2/addclient)
