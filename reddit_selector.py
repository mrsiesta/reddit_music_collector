from lib.reddit import Redditor
from lib.db_helper import sqliteHelper
from __future__ import unicode_literals
import youtube_dl


def get_latest(db_conn, channel):
    latest_youtube_content = [s for s in channel.new() if s.domain == 'youtube.com']
    return filter_latest(db_conn, latest_youtube_content)


def filter_latest(db_conn, submission_list):
    checked_list = []
    # For each item in list; check if submission id in database
    for sub in submission_list:
        if not db_conn.check_database_for_id(sub.id):
            checked_list.append(sub)

    return checked_list


def get_r_house_tracks_from_weekly(channel):
    # Get the weekly submissions
    weekly_roundups = channel.search('Your weekly', time_filter='all')
    weekly_submissions = [sub for sub in weekly_roundups]
    lines_to_parse = []
    for sub in weekly_submissions:
        for line in sub.selftext.split('\n'):
            if 'youtube.com' in line or 'youtu.be' in line:
                lines_to_parse.append(line)

    data = dict()
    for line in lines_to_parse:
        try:
            _, score, comments, link, links = line.split('| ')
        except Exception:
            continue
        title = link.split(']')[0].split('[')[1]
        youtube_url = link.split('](')[1][:-1]
        data[title] = {'score': int(score), 'youtube_url': youtube_url}

    # Order identified tracks by score
    ordered_tracks = sorted(data.items(), key=lambda item: item[1]['score'], reverse=True)
    return ordered_tracks


def fetch_undownloaded(db_conn, dest_path):
    db_conn.cursor.execute("select * from content where downloaded == false")
    data = db_conn.cursor.fetchall()
    print(f"Found {len(data)} tracks that need to be downloaded!\n")
    for row in data:
        print(f"DEBUG: Row data:\n[{row}]\n")
        _id, title, rank, ts, url, download = row

        # TODO extend database information to include artist and song title
        youtube_media_metadata = fetch_youtube_metadata(url)
        artist, song_title = parse_youtube_metadata(youtube_media_metadata)
        db_conn.update_db_with_track_data(_id, artist, song_title)

        print(f"Attempting to download {title}")
        mp3_path = download_youtube_track(url)
        if mp3_path:
            print(f"Successfully downloaded {title}")
            db_conn.mark_track_downloaded(_id)
            update_id3_tags(mp3_path, rank, artist, song_title)
            move_newly_downloaded(mp3_path, dest_path)
        else:
            print(f"Failed to download {title}")


def move_newly_downloaded(mp3_path, dest_dir):
    pass


def update_id3_tags(mp3_path, rank=None, artist=None, song_title=None):
    pass


def download_youtube_track(url):
    # Setup client
    class MyLogger(object):
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)

    def my_hook(d):
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }

    # Attempt to download and extract audio for youtube links
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            return True
        except Exception:
            print(f"Failed to download {url}")
            return False


def main():
    sql = sqliteHelper()
    r = Redditor()

    # Aggregate channel content
    house = r.reddit.subreddit("house")

    # Backport using the weekly aggregate postings
    # ordered_tracks = get_r_house_tracks_from_weekly(house)
    new_tracks = get_latest(sql, house)
    sql.update_database(new_tracks)
    fetch_undownloaded(sql)
