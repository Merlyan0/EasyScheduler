import os
import sqlite3


def create_connection() -> tuple:
    """
    Подключение к БД. Возвращает соединение к базе данных и курсор.
    """
    conn = sqlite3.connect(os.getcwd() + '/main.sqlite')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS reminders(
                     id integer PRIMARY KEY NOT NULL,
                     title text,
                     author int,                     
                     attachments text,
                     check_date date,
                     finished bool,
                    created_date date);""")
    conn.commit()
    return conn, cur


def add_to_db(conn, cur, title=None, author=None, attachments=None,
              check_date=None, finished=None, created_date=None) -> None:
    """
    Добавление нового значения в базу данных.
    """
    cur.execute(f"""INSERT INTO reminders(
                         title,
                         author,
                         attachments,
                         check_date,
                         finished,
                         created_date)
           VALUES (?, ?, ?, ?, ?, ?);""", (title, author, attachments, check_date, finished, created_date))
    conn.commit()


def set_date(conn, cur, author, date) -> None:
    """
    Задание даты для последнего напоминания пользователя.
    """
    cur.execute(f"SELECT * FROM reminders WHERE author={author} ORDER BY id DESC LIMIT 1")
    reminder_id = cur.fetchone()[0]
    cur.execute(f'UPDATE reminders SET check_date = ? WHERE id = ?', (date, reminder_id))
    conn.commit()
