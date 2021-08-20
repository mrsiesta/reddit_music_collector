#!/usr/bin/env python3

import argparse
import sys

from pathlib import Path

from lib.reddit import Redditor
from lib.db_helper import sqliteHelper
from lib.youtube_helper import YoutubeDL


def main():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-s', '--subreddit', required=True, help='The subreddit you want to scan')
    arg_parser.add_argument('-d', '--dest', help='The path you want to save downloaded files to')
    arg_parser.add_argument('--scan-only', dest='scan_only', action='store_true', default=False,
                            help="Don't download new tracks only scan and update the database")
    arg_parser.add_argument('--download-only', dest='download_only', action='store_true', default=False,
                            help="Don't scan for new tracks only fetch undownloaded content")
    arg_parser.add_argument('-m', '--del-failed', dest='del_failed', action='store_true', default=False,
                            help="Mark tracks that fail to download as downloaded so we no longer try to download them")
    arg_parser.add_argument('-l', '--list', action='store_true', default=False,
                            help="List the current contents of the database cache and exit")

    args = arg_parser.parse_args()

    sql = sqliteHelper()
    if args.list:
        sql.display_content_table()
        sys.exit()

    reddit = Redditor(sql)
    youtube = YoutubeDL(sql)

    # Update our database with latest youtube content
    if not args.download_only:
        reddit.update_cache(args.subreddit)

    # Collect youtube videos, extract audio, and move created mp3s to the requested destination path
    if not args.scan_only:
        youtube.fetch_undownloaded(args.dest, mark_failed_downloaded=args.del_failed)


if __name__ == "__main__":
    main()
