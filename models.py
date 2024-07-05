import sqlite3
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('auction.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Створення таблиці users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        last_name TEXT,
        first_name TEXT,
        phone_number TEXT,
        email TEXT UNIQUE,
        avatar TEXT
    )
    ''')

    # Створення таблиці topics
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        date_posted TIMESTAMP NOT NULL,
        user_id TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (username)
    )
    ''')

    # Створення таблиці posts
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

def add_user(username, password, last_name, first_name, phone_number, email, avatar=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO users (username, password, last_name, first_name, phone_number, email, avatar)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (username, password, last_name, first_name, phone_number, email, avatar))
    conn.commit()
    conn.close()

def add_topic(title, content, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO topics (title, content, date_posted, user_id)
    VALUES (?, ?, ?, ?)
    ''', (title, content, datetime.utcnow(), user_id))
    topic_id = cursor.lastrowid  # Отримуємо ID щойно створеної теми
    conn.commit()
    conn.close()
    return topic_id  # Повертаємо ID нової теми

def add_post(content, user_id, topic_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO posts (content, date_posted, user_id, topic_id)
    VALUES (?, ?, ?, ?)
    ''', (content, datetime.utcnow(), user_id, topic_id))
    conn.commit()
    conn.close()

# Викликаємо функцію для створення таблиць
create_tables()