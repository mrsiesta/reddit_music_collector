The Reddit Music Collector
==========================

This package will read the content of a reddit channel and collect links to music and reddit metadata.
Features of this software include:

 * Monitoring a reddit community for newly posted music
 * Check if the submission is for a new track and aggregate it's score
 * Weed out negatively scored content 
 * Automatically download new tracks from youtube


Configuration
=============
> **Must have python3 installed**
* Install requirements:

```
pip3 install pip-tools
pip-compile requirements.in
pip3 install -r requirements.txt
```

---

**Setup a reddit application to use the reddit API**
* [Create a reddit application for your user](https://www.reddit.com/prefs/apps/)
  - Scroll to the bottom of the page and click "are you a developer? create an app..."
  - Fill out the form for your new app
  - Use the data from the created app for your `praw.ini` file

---

**Setup praw.ini**
 - create a file called `praw.ini` in this directory using the following template:
```buildoutcfg
[DEFAULT]
# A boolean to indicate whether or not to check for package updates.
check_for_updates=True

# Object to kind mappings
comment_kind=t1
message_kind=t4
redditor_kind=t2
submission_kind=t3
subreddit_kind=t5
trophy_kind=t6

# The URL prefix for OAuth-related requests.
oauth_url=https://oauth.reddit.com

# The amount of seconds of ratelimit to sleep for upon encountering a specific type of 429 error.
ratelimit_seconds=5

# The URL prefix for regular requests.
reddit_url=https://www.reddit.com

# The URL prefix for short URLs.
short_url=https://redd.it

# The timeout for requests to Reddit in number of seconds
timeout=16

# Login details
client_id=<YourClientID Given after creating your reddit application>
client_secret=<clientSecret>
password=<the password for the user the reddit app was created with>
username=<the username your reddit app was created with>
```

---

Example of how to use this code
===============================
```
usage: reddit_selector.py [-h] -s SUBREDDIT [-d DEST] [--scan-only] [--download-only] [-l]

optional arguments:
  -h, --help            show this help message and exit
  -s SUBREDDIT, --subreddit SUBREDDIT
                        The subreddit you want to scan
  -d DEST, --dest DEST  The path you want to save downloaded files to
  --scan-only           Don't download new tracks only scan and update the database
  --download-only       Don't scan for new tracks only fetch undownloaded content
  -l, --list            List the current contents of the database cache and exit
```

* Check for any new submissions found on `/r/house` and download identified youtube content
> ./reddit_selector.py --subreddit=house --dest ~/Music/reddit_selections