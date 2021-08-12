The Reddit Music Collector
==========================

This package will read the content of a reddit channel and collect links to music and reddit metadata.
Features of this software include:

 * Monitoring a reddit community for newly posted music
 * Check if the submission is for a new track and aggregate it's score
 * Weed out negatively scored content 
 * Automatically download new tracks from youtube
 * Update the track metadata to include community score
 * Generate a youtube playlist

Configuration
=============

* Install requirements:
```pip3 install -r requirements.txt```

* [Create a reddit application for your user](https://www.reddit.com/prefs/apps/)
 - Scroll to the bottom of the page and click "are you a developer? create an app..."


* Setup praw.ini
 - create a file called praw.ini in the root directory using the following template:
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
client_id=Y4PJOclpDQy3xZ
client_secret=UkGLTe6oqsMk5nHCJTHLrwgvHpr
password=pni9ubeht4wd50gk
username=fakebot1
```