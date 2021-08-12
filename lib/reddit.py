import praw


class Redditor:
    def __init__(self):
        self.reddit = praw.Reddit(user_agent='Music Collection Bot User Agent')
