import praw


class Redditor:
    def __init__(self, db_conn):
        self.reddit = praw.Reddit(user_agent='Music Collection Bot User Agent')
        self.db_conn = db_conn

    def update_cache(self, subreddit):
        channel = self.reddit.subreddit(subreddit)
        latest_youtube_content = [s for s in channel.new(limit=500) if s.domain == 'youtube.com']
        new_content = self.filter_latest(latest_youtube_content)
        print(f"Found {len(new_content)} new youtube tracks on r/{subreddit}!")
        self.db_conn.update_database(new_content)

    def filter_latest(self, submission_list):
        return [s for s in submission_list if not self.db_conn.check_database_for_id(s.id)]