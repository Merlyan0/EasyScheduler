from datetime import datetime

import pymysql
from emoji import is_emoji
from pymysql.cursors import DictCursor

from config import *


class DataBase:

    def __init__(self):
        """
        Подключение к БД.
        """
        self.conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_DATABASE,
            charset='utf8mb4',
            cursorclass=DictCursor,
            autocommit=True,
            use_unicode=True
        )

        self.cur = self.conn.cursor()

        self.cur.execute("""CREATE TABLE IF NOT EXISTS reminders(
                         id integer AUTO_INCREMENT PRIMARY KEY,
                         title text,
                         author int,                     
                         attachments text,
                         check_date datetime,
                         need_notification bool,
                         finished bool,
                        created_date datetime);""")
        self.conn.commit()

        self.cur.execute('ALTER TABLE reminders CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_bin')
        self.conn.commit()

        print('EasyScheduler >', f'Подключение к базе данных {DB_DATABASE} успешно.')

    def add_to_db(self, title=None, author=None, attachments=None,
                  check_date=None, finished=None, created_date=datetime.now()) -> None:
        """
        Добавление нового значения в базу данных.
        """
        title = ''.join([i.encode('unicode-escape').decode('utf-8') if is_emoji(i) else i for i in title])

        self.cur.execute(f"""INSERT INTO reminders(
                             title,
                             author,
                             attachments,
                             check_date,
                             finished,
                             created_date)
               VALUES (%s, %s, %s, %s, %s, %s);""", (title, author, attachments, check_date, finished, created_date))
        self.conn.commit()

    def get_actual_reminders(self, date):
        self.cur.execute(f"SELECT * FROM reminders WHERE finished=0 and check_date=%s", (date, ))
        return self.cur.fetchall()

    def set_date(self, author, date) -> None:
        """
        Задание даты для последнего напоминания пользователя.
        """
        self.cur.execute(f"SELECT * FROM reminders WHERE author={author} ORDER BY id DESC LIMIT 1")
        reminder_id = self.cur.fetchone()['id']

        self.cur.execute(f'UPDATE reminders SET check_date = %s WHERE id = %s', (date, reminder_id))
        self.conn.commit()
