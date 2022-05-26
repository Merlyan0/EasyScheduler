from datetime import datetime, timedelta

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
            charset='utf8',
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
                         repeat_every int,
                         need_notification bool,
                         finished bool,
                         done bool,
                         created_date datetime);""")
        self.conn.commit()

        self.cur.execute("""CREATE TABLE IF NOT EXISTS users(
                                 id integer AUTO_INCREMENT PRIMARY KEY,
                                 user_id int,
                                 draw_limit int,
                                 voice_limit int,
                                 vip bool,
                                 last_update datetime,
                                 created_date datetime);""")
        self.conn.commit()

        self.conn.ping()

        print('EasyScheduler >', f'Подключение к базе данных {DB_DATABASE} успешно.')

    def add_to_db(self, title=None, author=None, attachments=None, check_date=None, repeat_every=-1,
                  need_notification=True, finished=False, done=False, created_date=datetime.now()) -> None:
        """
        Добавление нового значения в базу данных.
        """
        self.conn.ping()

        title = ''.join([i.encode('unicode-escape').decode('utf-8') if is_emoji(i) else i for i in title])

        self.cur.execute(f"""INSERT INTO reminders(
                             title,
                             author,
                             attachments,
                             check_date,
                             repeat_every,
                             need_notification,
                             finished,
                             done,
                             created_date)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""", (title, author, attachments, check_date, repeat_every,
                                                                 need_notification, finished, done, created_date))
        self.conn.commit()

    def get_actual_reminders(self, date_and_time: str, is_done=False) -> tuple:
        """
        Получить актуальные напоминания.
        """
        self.conn.ping()

        if is_done:
            self.cur.execute(f"SELECT * FROM reminders WHERE finished=0 and check_date<=%s and need_notification=1 and "
                             f"done=0",
                             (date_and_time,))

            return self.cur.fetchall()

        self.cur.execute(f"SELECT * FROM reminders WHERE finished=0 and check_date=%s and need_notification=1",
                         (date_and_time,))

        return self.cur.fetchall()

    def get_author_date_reminders(self, author: int, date: datetime) -> tuple:
        """
        Получить напоминания определенного автора по определенной дате.
        """
        self.conn.ping()

        self.cur.execute(f"""SELECT * FROM reminders WHERE finished=0 and check_date
                         >=%s AND check_date <=%s and author=%s""",
                         (date.strftime('%Y-%m-%d 00:00:00'), date.strftime('%Y-%m-%d 23:59:59'), author))

        return self.cur.fetchall()

    def get_author_reminders(self, author: int) -> tuple:
        """
        Получить напоминания от определенного автора.
        """
        self.conn.ping()

        self.cur.execute(f"""SELECT * FROM reminders WHERE finished=0 and author=%s""",
                         (author,))

        return self.cur.fetchall()

    def set_date(self, author: int, date: str) -> None:
        """
        Задание даты для последнего напоминания пользователя.
        """
        self.conn.ping()

        self.cur.execute(f"SELECT * FROM reminders WHERE author={author} ORDER BY id DESC LIMIT 1")
        reminder_id = self.cur.fetchone()['id']

        self.cur.execute('UPDATE reminders SET check_date = %s WHERE id = %s',
                         (date, reminder_id))
        self.conn.commit()

        self.cur.execute('UPDATE reminders SET need_notification = 1 WHERE id = %s',
                         (reminder_id,))
        self.conn.commit()

    def set_finished(self, list_of_id: list) -> None:
        """
        Отметить напоминания завершенными.
        """
        self.conn.ping()

        for i in list_of_id:
            self.cur.execute('UPDATE reminders SET finished = 1 WHERE id = %s', (i,))
            self.conn.commit()

    def set_delayed(self, reminder_id: int) -> None:
        """
        Отметить напоминания отложенными.
        """
        self.conn.ping()

        self.cur.execute('SELECT * FROM reminders WHERE id = %s', (reminder_id,))
        update_date = self.cur.fetchone()['check_date'] + timedelta(minutes=5)

        self.cur.execute('UPDATE reminders SET check_date = %s WHERE id = %s', (update_date, reminder_id))
        self.conn.commit()

        self.cur.execute('UPDATE reminders SET done = 0 WHERE id = %s', (reminder_id,))
        self.conn.commit()

    def get_reminder(self, reminder_id: int) -> tuple:
        """
        Получить напоминание по id.
        """
        self.conn.ping()

        self.cur.execute('SELECT * FROM reminders WHERE id = %s', (reminder_id,))
        return self.cur.fetchone()

    def add_user(self, user_id: int) -> None:
        """
        Добавить пользователя в БД.
        """
        self.conn.ping()

        self.cur.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        if not self.cur.fetchone():
            self.cur.execute(f"""INSERT INTO users(
                                 user_id,
                                 draw_limit,
                                 voice_limit,
                                 vip,
                                 last_update,
                                 created_date)
                           VALUES (%s, %s, %s, %s, %s, %s);""", (user_id, 0, 0, False, datetime.now(), datetime.now()))
            self.conn.commit()

    def get_user_draw_limit(self, user_id: int) -> int:
        """
        Возвращает лимит рисования конкретного пользователя в БД.
        """
        self.conn.ping()

        self.cur.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        return self.cur.fetchone()['draw_limit']

    def get_user_voice_limit(self, user_id: int) -> int:
        """
        Возвращает лимит аудио сообщений конкретного пользователя в БД.
        """
        self.conn.ping()

        self.cur.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        return self.cur.fetchone()['voice_limit']

    def add_to_draw_limit(self, user_id: int, n=1) -> None:
        """
        Добавить n-ное количество попыток к лимиту на рисование пользователя.
        """
        self.conn.ping()

        self.cur.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        update_limit = self.cur.fetchone()['draw_limit'] + n

        self.cur.execute('UPDATE users SET draw_limit = %s WHERE user_id = %s', (update_limit, user_id))
        self.conn.commit()

    def add_to_voice_limit(self, user_id: int, n=1) -> None:
        """
        Добавить n-ное количество попыток к лимиту на голосовые сообщения пользователя.
        """
        self.conn.ping()

        self.cur.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        update_limit = self.cur.fetchone()['voice_limit'] + n

        self.cur.execute('UPDATE users SET voice_limit = %s WHERE user_id = %s', (update_limit, user_id))
        self.conn.commit()

    def update_limits(self, user_id: int) -> None:
        """
        Каждодневное обновление лимитов у пользователей.
        """
        self.conn.ping()

        self.cur.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))

        if self.cur.fetchone()['last_update'].strftime("%d.%m.%Y") != datetime.now().strftime("%d.%m.%Y"):
            self.cur.execute('UPDATE users SET draw_limit = 0 WHERE user_id = %s', (user_id,))
            self.conn.commit()

            self.cur.execute('UPDATE users SET voice_limit = 0 WHERE user_id = %s', (user_id,))
            self.conn.commit()

            self.cur.execute('UPDATE users SET last_update = %s WHERE user_id = %s', (datetime.now(), user_id))
            self.conn.commit()

    def set_done(self, reminder_id: int) -> None:
        """
        Отметить напоминание "напомненным".
        """
        self.conn.ping()

        self.cur.execute('UPDATE reminders SET done = 1 WHERE id = %s', (reminder_id,))
        self.conn.commit()

    def repeat(self, reminder_id: int) -> None:
        """
        Заменить дату напоминания на необходимую дату его повтора.
        """
        self.conn.ping()

        self.cur.execute('SELECT * FROM reminders WHERE id = %s', (reminder_id,))
        reminder = self.cur.fetchone()
        repeat_every = reminder['repeat_every']
        date = reminder['check_date']
        if repeat_every == -1:
            return

        if repeat_every == -2:
            if date.day != 29 and date.month != 2:
                update_date = date.replace(year=date.year + 1)
            else:
                update_date = date.replace(day=28, year=date.year + 1)

        elif repeat_every == -3:
            if date.day >= 29 and date.month + 1 == 2:
                update_date = date.replace(day=28, month=date.month + 1)
            else:
                try:
                    update_date = date.replace(month=date.month + 1)

                except ValueError:
                    update_date = date.replace(day=date.day - 1, month=date.month + 1)

        else:
            update_date = date + timedelta(days=int(repeat_every))

        self.cur.execute('UPDATE reminders SET check_date = %s WHERE id = %s', (update_date, reminder_id))
        self.conn.commit()

    def repeat_all(self):
        """
        Заменить дату у всех неотмеченных напоминаний.
        """
        self.conn.ping()

        self.cur.execute('SELECT * FROM reminders WHERE need_notification = 0 and finished = 0')

        for i in self.cur.fetchall():
            if i['repeat_every'] == -1:
                continue

            if i['repeat_every'] == -2:
                if i['check_date'].day != 29 and i['check_date'].month != 2:
                    update_date = i['check_date'].replace(year=i['check_date'].year + 1)
                else:
                    update_date = i['check_date'].replace(day=28, year=i['check_date'].year + 1)

            elif i['repeat_every'] == -3:
                if i['check_date'].day >= 29 and i['check_date'].month + 1 == 2:
                    update_date = i['check_date'].replace(day=28, month=i['check_date'].month + 1)
                else:
                    try:
                        update_date = i['check_date'].replace(month=i['check_date'].month + 1)

                    except ValueError:
                        update_date = i['check_date'].replace(day=i['check_date'].day - 1,
                                                              month=i['check_date'].month + 1)

            else:
                update_date = i['check_date'] + timedelta(days=i['repeat_every'])

            if update_date.day == datetime.now().day:
                self.cur.execute('UPDATE reminders SET check_date = %s WHERE id = %s', (update_date, i['id']))
                self.conn.commit()
