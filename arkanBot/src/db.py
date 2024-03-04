from pickle import TRUE
import sqlite3
import uuid
import pandas as pd
from datetime import datetime
# from openpyxl import Workbook
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
# cursor.execute("ALTER TABLE users ADD COLUMN file_sent BOOLEAN DEFAULT FALSE;")
# cursor.execute(
#     "ALTER TABLE users ADD COLUMN feedback_choice TEXT DEFAULT NULL;")
# cursor.execute(
# "ALTER TABLE users ADD COLUMN alredy_recive_one TEXT DEFAULT NULL")
# cursor.execute("ALTER TABLE users ADD COLUMN march_send BOOLEAN DEFAULT FALSE")
# cursor.execute("ALTER TABLE users ADD COLUMN march_sphere_chosen TEXT DEFAULT NULL")
# cursor.execute("ALTER TABLE users ADD COLUMN march_send_all BOOLEAN DEFAULT FALSE")
# cursor.execute("ALTER TABLE users ADD COLUMN no_friend BOOLEAN DEFAULT FALSE")
# conn.commit()

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
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS gifts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        already_take BOLEAN DEFAULT FALSE,
        gift_date TEXT DEFAULT NULL
    )
"""
)

conn.commit()

def db_no_friend(id):
    cursor.execute(
        "UPDATE users SET no_friend = ? WHERE user_id = ?", (TRUE, id)
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
    conn.commit()

def what_choose_in_march(id):
    return cursor.execute(
        "SELECT march_sphere_chosen FROM users WHERE chat_id = ?", (id,)).fetchone()
    
def set_already_recive_one(chat_id):
    cursor.execute(
        "UPDATE users SET alredy_recive_one = ? WHERE chat_id = ?", (
            "True", chat_id,)
    )
    conn.commit()
    
def set_already_recive_all_march(chat_id):
    cursor.execute(
        "UPDATE users SET march_send_all = ? WHERE chat_id = ?", (
            "True", chat_id,)
    )
    conn.commit()


def set_discount_end(chat_id, discount_end):
    cursor.execute(
        "UPDATE users SET discount_end = ? WHERE chat_id = ?", (
            discount_end, chat_id,)
    )
    conn.commit()


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

def get_nik(id):
    # Выполняем запрос для проверки статуса получения всех файлов пользователем
    cursor.execute(
        "SELECT username FROM users WHERE user_id = ?", (
            id,)
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


########################################
def get_gift_date():
    cursor.execute("""
    SELECT DISTINCT  CASE WHEN username NOT NULL then username ELSE gifts.user_id END AS username, gifts.user_id, gifts.gift_date
    FROM gifts, users
    WHERE users.user_id = gifts.user_id and user_id <> 740905109 and user_id <> 1358227914;
""")

def get_active_users():
    cursor.execute("""
    SELECT DISTINCT  CASE WHEN username NOT NULL then username ELSE user_id END AS username, user_id
    FROM users
    WHERE march_send <> 0 and user_id <> 740905109 and user_id <> 1358227914;
""")
    
def get_not_active_users():
    cursor.execute("""
    SELECT DISTINCT  CASE WHEN username NOT NULL then username ELSE user_id END AS username, user_id
    FROM users
    WHERE march_send = 0 and user_id <> 740905109 and user_id <> 1358227914;
""")
    
def get_button_users():
    cursor.execute("""
    SELECT DISTINCT  CASE WHEN username NOT NULL then username ELSE user_id END AS username, user_id
    FROM users 
    WHERE no_friend <> 0 and user_id <> 740905109 and user_id <> 1358227914;
""")

def get_reference_users():
    cursor.execute("""
    SELECT DISTINCT  CASE WHEN username NOT NULL then username ELSE user_id END AS username, user_id
    FROM users 
    WHERE march_send_all <> 0 and user_id <> 740905109 and user_id <> 1358227914;
""")
    
def get_number_all_users_march():
    cursor.execute("""
    SELECT  count(user_id)
    FROM users
    WHERE march_send <> 0 and user_id <> 740905109 and user_id <> 1358227914;                   
""")
def get_number_all_users_past():
        cursor.execute("""
    SELECT  count(user_id)
    FROM users
    WHERE file_sent <> 0 and user_id <> 740905109 and user_id <> 1358227914;                   
""")
        
def make_excel_file(base_excel_path):
    # Запросы и имена листов для каждого запроса
    queries_and_sheets = [
        ("""
        SELECT DISTINCT  CASE WHEN username NOT NULL then username ELSE gifts.user_id END AS username, gifts.user_id, gifts.gift_date
        FROM gifts, users
        WHERE users.user_id = gifts.user_id and gifts.user_id <> 740905109 and gifts.user_id <> 1358227914;""", "Имя и дата купона"),
        ("""
        SELECT DISTINCT  CASE WHEN username NOT NULL then username ELSE user_id END AS username, user_id
        FROM users
        WHERE march_send <> 0 and user_id <> 740905109 and user_id <> 1358227914;""", "Активные пользователи"),
        ("""
        SELECT DISTINCT  CASE WHEN username NOT NULL then username ELSE user_id END AS username, user_id
        FROM users
        WHERE march_send = 0 and user_id <> 740905109 and user_id <> 1358227914;""", "Не активные пользователи"),
        ("""
        SELECT DISTINCT  CASE WHEN username NOT NULL then username ELSE user_id END AS username, user_id
        FROM users 
        WHERE no_friend <> 0 and user_id <> 740905109 and user_id <> 1358227914;""", "Нажали кнопку"),
        ("""
        SELECT DISTINCT  CASE WHEN username NOT NULL then username ELSE user_id END AS username, user_id
        FROM users 
        WHERE march_send_all <> 0 and user_id <> 740905109 and user_id <> 1358227914;""", "Отправили ссылку"),
        ("""
        SELECT  count(user_id)
        FROM users
        WHERE march_send <> 0 and user_id <> 740905109 and user_id <> 1358227914;""", "Не удалили после второй рассылки"),
        ("""
        SELECT  count(user_id)
        FROM users
        WHERE file_sent <> 0 and user_id <> 740905109 and user_id <> 1358227914;""", "Не удалили после первой рассылки")
        # Добавьте больше запросов и имен листов по необходимости
    ]

    # Получение текущего времени для создания уникального имени файла
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    excel_path = f'{base_excel_path}_{current_time}.xlsx'

    # Создание объекта Excel writer с использованием Pandas
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for sql_query, sheet_name in queries_and_sheets:
            # Чтение результатов запроса в DataFrame
            df = pd.read_sql_query(sql_query, conn)
            # Запись DataFrame на отдельный лист
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    # conn.close()  # Не забудьте закрыть подключение к базе данных

    print(f'Данные успешно экспортированы в {excel_path} на разные листы')
    return excel_path