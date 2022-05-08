import sqlite3


def create_connection() -> tuple:
    """
    Возвращает соединение к базе данных и курсор.
    """
    conn = sqlite3.connect('main.sqlite')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS reminders(
                     id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                     title ntext,
                     author int,                     
                     attachments ntext,
                     check_date date,
                     finished bool,
                    created_date date);""")
    conn.commit()
    return conn, cur


def add_to_db(conn, cur, title=None, author=None, attachments=None, check_date=None, finished=None, created_date=None) -> None:
    """
    Добавить новое значение в базу данных.
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



