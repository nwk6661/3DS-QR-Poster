# 3DS-QR-Poster

A python3 bot that creates and posts QR codes to reddit for new 3DS hombrebrew posted on the /r/3DShacks subreddit.

    pip install requests
    pip install praw
    pip install praw-oauth2util
    pip install humanize

    
You will need to [set up oauth2util](https://github.com/SmBe19/praw-OAuth2Util/blob/master/OAuth2Util/README.md)  
Create a file called `github_credentials.txt` containing
```
username
password
```

and nothing else (no newline at end)

Big thanks to /u/codepoet82 for help with SMDH data, github auth, API help, and other things.