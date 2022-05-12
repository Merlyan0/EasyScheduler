import pymysql
from pymysql.cursors import DictCursor

from config import *


def create_connection() -> tuple:
    """
    Подключение к БД. Возвращает соединение к базе данных и курсор.
    """
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_DATABASE,
        charset='utf8mb4',
        cursorclass=DictCursor
    )
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS reminders(
                     id integer AUTO_INCREMENT PRIMARY KEY,
                     title text,
                     author int,                     
                     attachments text,
                     check_date datetime,
                     finished bool,
                    created_date datetime);""")
    conn.commit()

    print('Подключение к базе данных успешно!')

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
           VALUES (%s, %s, %s, %s, %s, %s);""", (title, author, attachments,
                                                 check_date, finished, created_date))
    conn.commit()


def set_date(conn, cur, author, date) -> None:
    """
    Задание даты для последнего напоминания пользователя.
    """
    cur.execute(f"SELECT * FROM reminders WHERE author={author} ORDER BY id DESC LIMIT 1")
    reminder_id = cur.fetchone()['id']
    
    cur.execute(f'UPDATE reminders SET check_date = %s WHERE id = %s', (date, reminder_id))
    conn.commit()
