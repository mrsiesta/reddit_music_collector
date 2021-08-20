import shutil
import signal
import youtube_dl

from pathlib import Path


class TimeoutError(Exception):
    pass


def timeout_handler():
    print("Timed Out!")
    raise TimeoutError("Timed out, exiting process...")


class YoutubeDL:
    def __init__(self, db_conn):
        signal.signal(signal.SIGALRM, timeout_handler)
        self.db_conn = db_conn

    def fetch_undownloaded(self, dest_path="~/Music/reddit", mark_failed_downloaded=False):
        data = self.db_conn.fetch_undownloaded()
        print(f"Found {len(data)} tracks that need to be downloaded!\n")
        for row in data:
            signal.alarm(60)
            _id, _subreddit, title, artist, track_name, rank, ts, url, download = row

            if rank < 1:
                self.db_conn.mark_track_downloaded(_id)
                continue

            print(f"Attempting to download [{title}]")
            try:
                youtube_data = self.download_and_extract_audio(url)

                if not youtube_data:
                    if mark_failed_downloaded:
                        self.db_conn.mark_track_downloaded(_id)
                    print(f"Failed to download [{title}]")
                    print('-' * 80 + '\n')
                    continue

                self.db_conn.mark_track_downloaded(_id)
                # Anything over 15 minutes is likely not a single track, discard anything longer than 15 minutes
                track_length = youtube_data.get('duration', 0)
                mp3_path = self.search_log_data_for_mp3_path()
                if not 120 < track_length < 900:
                    print(f"Track duration [{track_length}] is outside of allowed duration, deleting file [{mp3_path}]")
                    Path(mp3_path).unlink(missing_ok=True)
                    print('-' * 80 + '\n')
                    continue

                if mp3_path:
                    print(f"Successfully downloaded {title}")
                    self.move_newly_downloaded(mp3_path, Path(dest_path).joinpath(_subreddit))
                else:
                    print(f"Failed to download {title}")
            except TimeoutError:
                print('-' * 80 + '\n')
                continue

            signal.alarm(0)
            print('-'*80 + '\n')

            # TODO extend database information to include artist and song title
            # youtube_media_metadata = self.fetch_youtube_metadata(url)
            # artist, song_title = self.parse_youtube_metadata(youtube_media_metadata)
            # self.db_conn.update_db_with_track_data(_id, artist, song_title)
            # self.update_id3_tags(mp3_path, rank, artist, song_title)

    def search_log_data_for_mp3_path(self):
        for line in self.log_data:
            if '[ffmpeg] Destination:' in line:
                return line.replace('[ffmpeg] Destination: ', '')

    def fetch_youtube_metadata(self, url):
        pass

    @staticmethod
    def move_newly_downloaded(mp3_file, dest_dir):
        if Path(dest_dir).exists() and not Path(dest_dir).is_dir():
            raise RuntimeError(f"Destination path [{dest_dir}] is not a directory")
        if not Path(mp3_file).is_file():
            raise RuntimeError(f"File at path [{mp3_file}] does not exist")
        if not Path(dest_dir).exists():
            Path(dest_dir).mkdir(parents=True, exist_ok=True)

        print(f"Moving [{mp3_file}] to {dest_dir}")
        shutil.move(Path(mp3_file).absolute(), Path(dest_dir).joinpath(mp3_file))

    def parse_youtube_metadata(self, metadata):
        return "", ""

    def update_id3_tags(self, mp3_path, rank=None, artist=None, song_title=None):
        pass

    def download_and_extract_audio(self, url):
        # Set the timeout for this function to 3 minutes
        signal.alarm(180)
        self.log_data = []

        class MyLogger(object):
            def __init__(self, log_capture):
                self.log_capture = log_capture

            def debug(self, msg):
                self.log_capture.append(msg)

            def warning(self, msg):
                pass

            def error(self, msg):
                print(msg)

        def my_hook(d):
            if d['status'] == 'finished':
                print('Done downloading, now converting ...')

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'dump_single_json': True,
            'forcefilename': True,
            'logger': MyLogger(self.log_data),
            'progress_hooks': [my_hook],
        }

        # Attempt to download and extract audio for youtube links
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                result = ydl.extract_info(url)
                signal.alarm(0)
                return result
            except Exception as e:
                print(f"Failed to download {url}\nException: {e}")
                signal.alarm(0)
                return False
