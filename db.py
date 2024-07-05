import sqlite3

def get_db_connection():
    conn = sqlite3.connect('auction.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        last_name TEXT,
        first_name TEXT,
        phone_number TEXT,
        email TEXT,
        avatar TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lots (
        id TEXT PRIMARY KEY,
        name TEXT,
        description TEXT,
        start_price REAL,
        created_at TEXT,
        owner TEXT,
        image_urls TEXT,
        user_ip TEXT,
        current_price REAL,
        times INTEGER,
        end_date TIMESTAMP,
        category_id TEXT,
        FOREIGN KEY(owner) REFERENCES users(username) ON DELETE CASCADE
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        date_posted TIMESTAMP NOT NULL,
        user_id TEXT NOT NULL,
        topic_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (username),
        FOREIGN KEY (topic_id) REFERENCES topics (id)
    )
    ''')

    conn.commit()
    conn.close()

# Викликаємо функцію для створення таблиць
create_tables()