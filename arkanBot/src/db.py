import sqlite3
import uuid

# Подключение к базе данных
conn = sqlite3.connect("../db/mydatabase.db")
cursor = conn.cursor()

# Создание таблицы пользователей с полем chat_id
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        user_id INTEGER,
        chat_id INTEGER,
        arcan INTEGER DEFAULT NULL,
        referral_code TEXT
    )
"""
)

# cursor.execute(
# "ALTER TABLE users ADD COLUMN already_have_all_files TEXT DEFAULT NULL")
# cursor.execute("ALTER TABLE users ADD COLUMN birth_date TEXT DEFAULT NULL")
# cursor.execute("ALTER TABLE users ADD COLUMN like TEXT DEFAULT NULL")
# cursor.execute("ALTER TABLE users ADD COLUMN first_name TEXT DEFAULT NULL")
# cursor.execute("ALTER TABLE users ADD COLUMN discount_end TEXT DEFAULT NULL")
# cursor.execute("ALTER TABLE users ADD COLUMN first_meet TEXT DEFAULT NULL")
cursor.execute("ALTER TABLE users ADD COLUMN file_sent BOOLEAN DEFAULT FALSE;")
cursor.execute(
    "ALTER TABLE users ADD COLUMN feedback_choice TEXT DEFAULT NULL;")
# cursor.execute(
# "ALTER TABLE users ADD COLUMN alredy_recive_one TEXT DEFAULT NULL")


# Создание таблицы для отслеживания переходов по реферальным ссылкам
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY,
        referrer_id INTEGER,
        referred_id INTEGER,
        FOREIGN KEY (referrer_id) REFERENCES users (id),
        FOREIGN KEY (referred_id) REFERENCES users (id)
    )
"""
)

conn.commit()


def generate_referral_code():
    return str(uuid.uuid4())


def add_user(username, chat_id, referral_code=None):
    cursor.execute(
        "INSERT INTO users (username, chat_id, referral_code) VALUES (?, ?, ?)",
        (username, chat_id, referral_code),
    )
    conn.commit()
    return cursor.lastrowid


def add_points(user_id, points):
    cursor.execute(
        "UPDATE users SET points = points + ? WHERE id = ?", (points, user_id)
    )
    conn.commit()


def set_birth_date(chat_id, birth_date):
    cursor.execute(
        "UPDATE users SET first_name = ? WHERE chat_id = ?", (
            birth_date, chat_id,)
    )


def set_already_recive_one(chat_id):
    cursor.execute(
        "UPDATE users SET alredy_recive_one = ? WHERE chat_id = ?", (
            "True", chat_id,)
    )


def set_discount_end(chat_id, discount_end):
    cursor.execute(
        "UPDATE users SET discount_end = ? WHERE chat_id = ?", (
            discount_end, chat_id,)
    )


def check_if_user_received_one_file(user_id):
    cursor = conn.cursor()

    # Выполняем запрос для проверки статуса получения всех файлов пользователем
    cursor.execute(
        "SELECT alredy_recive_one FROM users WHERE user_id = ?", (
            user_id,)
    )
    result = cursor.fetchone()

    # Возвращаем результат проверки
    return result[0] if result else None


def check_if_user_received_all_files(user_id):
    cursor = conn.cursor()

    # Выполняем запрос для проверки статуса получения всех файлов пользователем
    cursor.execute(
        "SELECT already_have_all_files FROM users WHERE user_id = ?", (
            user_id,)
    )
    result = cursor.fetchone()

    # Возвращаем результат проверки
    return result[0] if result else None

# def add_discount_end
# def add_date
