import sqlite3

DB_PATH = 'example.db'

def create_users_table():
    """Создаёт таблицу users, если она не существует."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        ''')
        conn.commit()
    print("Таблица users успешно создана (если её не было).")

if __name__ == "__main__":
    create_users_table()
