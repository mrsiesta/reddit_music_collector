import sqlite3
import tabulate
import time

from sqlite3 import Error


class sqliteHelper:

    def __init__(self, sqlite_path='content-cache.db', ):
        """Initialize our database and ensure the required tables exist"""
        required_tables = {
            'content': {
                'create_statement':
                    """ CREATE TABLE IF NOT EXISTS content (
                            id text PRIMARY KEY,
                            subreddit text,
                            title text NOT NULL,
                            artist text,
                            song_title text,
                            rank integer,
                            submission_date integer,
                            url text,
                            downloaded bool
                        ); 
                    """
            }
        }

        self.db_conn = self.create_connection(sqlite_path)
        self.cursor = self.db_conn.cursor()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in self.cursor.fetchall()]

        for table_name, table_data in required_tables.items():
            if table_name not in tables:
                self.create_table(table_data['create_statement'])

    @staticmethod
    def create_connection(db_file_path):
        """ create a database connection to a SQLite database """
        try:
            conn = sqlite3.connect(db_file_path)
            return conn
        except Error as e:
            print(e)
            raise e

    def create_table(self, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            self.cursor.execute(create_table_sql)
        except Error as e:
            print(e)

    def display_content_table(self):
        self.cursor.execute("SELECT * from content")
        content_rows = self.cursor.fetchall()

        self.cursor.execute('PRAGMA table_info(content)')
        table_columns = self.cursor.fetchall()
        headers = [row[1] for row in table_columns]

        print(tabulate.tabulate(content_rows, headers=headers, tablefmt='fancy'))

    def insert_content(self, data):
        sql = ''' INSERT INTO content(id,subreddit,title,rank,submission_date,url,downloaded)
                VALUES(?,?,?,?,?,?,?) '''
        self.cursor.execute(sql, data)
        self.db_conn.commit()
        return self.cursor.lastrowid

    def update_database(self, track_list):
        print("Updating content table with new tracks")
        for new_track in track_list:
            _id = new_track.id
            _subreddit = new_track.subreddit.display_name
            _title = new_track.title
            _rank = int(new_track.score)
            _date = time.strftime('%Y/%m/%d %X', time.localtime(float(new_track.created)))
            _url = new_track.url_overridden_by_dest
            _downloaded = False
            _data = (_id, _subreddit, _title, _rank, _date, _url, _downloaded)
            self.insert_content(_data)

        print("Done inserting new data")

    def mark_track_downloaded(self, id):
        self.cursor.execute(f"UPDATE content SET downloaded = 1 WHERE id == '{id}'")
        self.db_conn.commit()

    def check_database_for_id(self, id):
        self.cursor.execute(f"SELECT id from content where id == '{id}'")
        result = self.cursor.fetchall()
        if result:
            return True

        return False

    def update_db_with_track_data(self, id, artist, song_title):
        pass

    def fetch_undownloaded(self):
        self.cursor.execute("select * from content where downloaded == false")
        return self.cursor.fetchall()
