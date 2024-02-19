import asyncio
from telegram import InputFile
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from dateparser.search.search import DateSearchWithDetection
import re
import dateparser
import logging
from telegram import Update
import os
from glob import glob
from telegram.ext import (
    # Updater,
    MessageHandler,
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)
from datetime import datetime, timedelta
from db import *
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

# cursor.execute("ALTER TABLE users ADD COLUMN already_have_all_files TEXT DEFAULT NULL")
# cursor.execute("ALTER TABLE users ADD COLUMN birth_date TEXT DEFAULT NULL")
# cursor.execute("ALTER TABLE users ADD COLUMN like TEXT DEFAULT NULL")
# cursor.execute("ALTER TABLE users ADD COLUMN first_name TEXT DEFAULT NULL")


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


load_dotenv()

TOKEN = os.getenv("TOKEN")


def clean_filename(filename):
    # Разделяем имя файла и расширение
    name, ext = os.path.splitext(filename)
    sphere = name[-1]
    if sphere == "0":
        sphere = "Отношения"
    elif sphere == "1":
        sphere = "Финансы"
    elif sphere == "2":
        sphere = "Саморазвитие"

    # Находим первую группу цифр (номер аркана)
    arcan_number_match = re.search(r"\d+", name)
    if arcan_number_match:
        arcan_number = arcan_number_match.group()
        # Удаляем все цифры и подчеркивания, кроме первой найденной группы цифр
        clean_name = re.sub(r"(_+)", " ", name)
        clean_name = re.sub(r"\b\d+\b", "", clean_name)
        # clean_name = f"{arcan_number} Аркан {clean_name}"
        clean_name = f"{arcan_number} Аркан {sphere}"
    else:
        # Если не найдено цифр, просто удаляем подчеркивания
        clean_name = re.sub(r"(_+)", " ", name)

    # Возвращаем обработанное имя файла с расширением
    return clean_name.strip() + ext


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def parse_date(date_str):

    if parsed_date := dateparser.parse(date_str, languages=["ru"]):
        return parsed_date.date()
    else:
        return None


def generate_pdf_path(arcan, try_, type):
    pdf_directory = "../misk/"
    if type:
        if pdf_files := glob(os.path.join(pdf_directory, f"{arcan}_*{type}.pdf")):
            try:
                return pdf_files[try_]
            except:
                return None
        else:
            return None
    elif pdf_files := glob(os.path.join(pdf_directory, f"{arcan}_*.pdf")):
        return pdf_files
    else:
        return None


async def send_arcan(
    update: Update, context: ContextTypes.DEFAULT_TYPE, arcan, type, refer=None
):
    if not type:
        all_pdf = generate_pdf_path(arcan, 0, None)
        for pdf in all_pdf:
            with open(pdf, "rb") as pdf_file:
                new_filename = clean_filename(os.path.basename(pdf))
                await context.bot.send_document(
                    chat_id=refer,
                    document=InputFile(pdf_file, filename=new_filename),
                    caption="",
                )
        # await context.bot.send_message(
        #     chat_id=refer,
        #     text="Если у тебя остались вопросы или ты хочешь глубже разобрать сферы своей жизни, то пиши мне в личные сообщения @polinaataroo\n💌",
        # )
    else:
        for i in range(3):
            if pdf_path := generate_pdf_path(arcan, i, type):
                with open(pdf_path, "rb") as pdf_file:
                    new_filename = clean_filename(os.path.basename(pdf_path))
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=InputFile(pdf_file, filename=new_filename),
                        caption="",
                    )


def calculate_arcan(date):
    # Расчет аркана
    while date > 22:
        date = date - 22
    return date


def extract_digit_substring(input_string):
    if matches := re.findall(r"\d+", input_string):
        start_index = input_string.index(matches[0])
        end_index = input_string.rindex(matches[-1]) + len(matches[-1])
        return input_string[start_index:end_index]
    else:
        return input_string


def first_try_pars(message):
    maybe_date = extract_digit_substring(message)
    res = parse_date(maybe_date)
    if res is None:
        res = parse_date(message)
    return res


def second_try_pars(message: str):
    _search_with_detection = DateSearchWithDetection()
    result = _search_with_detection.search_dates(message, languages=["ru"])
    result = result.get("Dates")
    if result == [] or result is None:
        return None
    birth_date = replace_shit_from_string(str(result[0][1]))
    print(f"BIRTH DATE ={birth_date}")
    return birth_date


def replace_shit_from_string(str: str):
    return (
        str.replace("-", "")
        .replace(" ", "")
        .replace(":", "")
        .replace("0", "")
        .replace(",", "")
    )


async def check_subscription(
    update: Update, context: ContextTypes.DEFAULT_TYPE, channel_id
):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(channel_id, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
    return False


async def ask_to_invite_friend(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user
):
    user_id = update.effective_user.id
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Я уже рассказала тебе про одну сферу.\nЕсли интересны остальные -- отправь другу эту ссылку:\n\n{referral_link} \n\nи как только он зарегистрируется, я отправлю тебе оставшиеся материалы ✨",
        # reply_markup=reply_markup,
    )


async def handle_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if context.user_data.get("was_met"):
        return
    message = update.message.text
    # Сохраняем дату в user_data
    context.user_data["temporary_birth_date"] = message
    # Сохраняем дату в user_data
    context.user_data["temporary_update"] = update
    context.user_data["temporary_user"] = user  # Сохраняем дату в user_data
    # context.user_data["temporary_contex"] = update  # Сохраняем дату в user_data

    # Создаем клавиатуру для подтверждения даты рождения
    keyboard = [
        [InlineKeyboardButton("Да", callback_data="confirm_date_yes")],
        [InlineKeyboardButton("Нет", callback_data="confirm_date_no")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Так как у вас всего одна попытка, проверьте свою дату рождения. Всё верно?\nВаша дата: {message}",
        reply_markup=reply_markup,
    )


async def confirm_birthday_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data = context.user_data
    if query.data == "confirm_date_no":
        # Ожидаем новой даты рождения
        await context.bot.delete_message(
            chat_id=query.message.chat_id, message_id=query.message.message_id
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Хорошо, пожалуйста, отправьте мне корректную дату рождения🙏🏼",
        )
        user_data["awaiting_new_birth_date"] = True
    elif query.data == "confirm_date_yes":
        await context.bot.delete_message(
            chat_id=query.message.chat_id, message_id=query.message.message_id
        )
        context.user_data["was_met"] = True
        # Получаем сохраненную дату
        message = user_data.get("temporary_birth_date")
        birth_date = first_try_pars(message)
        # user = update.message.from_user
        user_data = context.user_data
        await notify_new_user(user_data.get("temporary_update"), context, message)
        context.user_data["real_birth_date"] = message
        birth_date = first_try_pars(message)
        # context.user_data["user"] = user
        context.user_data["user"] = user_data.get("temporary_user")
        context.user_data["already_in"] = 1
        context.user_data["is_robot_sure"] = ""
        if birth_date is None:
            context.user_data[
                "is_robot_sure"
            ] = "Я не уверен и скорее всего ошибаюсь, но возможно это правильный аркан, лучше проверь: "
            birth_date = second_try_pars(message)
        else:
            birth_date = replace_shit_from_string(str(birth_date))
            message = user_data["real_birth_date"]
            birth_date = first_try_pars(message)
        birth_date = (
            second_try_pars(message)
            if birth_date is None
            else replace_shit_from_string(str(birth_date))
        )
        user_data["birth_date"] = birth_date

        # Создаем клавиатуру для выбора сферы
        keyboard = [
            [InlineKeyboardButton("Отношения❤️", callback_data="0")],
            [InlineKeyboardButton("Финансы💸", callback_data="1")],
            [InlineKeyboardButton("Саморазвитие📚", callback_data="2")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Пожалуйста, выберите один из вариантов:",
            reply_markup=reply_markup,
        )


# https://t.me/polinabelyaewa
def increment_counter(
    update: Update, context: ContextTypes.DEFAULT_TYPE, counter_name: str
):
    chat_id = update.effective_chat.id
    context.bot_data.setdefault(counter_name, {}).setdefault(chat_id, 0)
    context.bot_data[counter_name][chat_id] += 1


def get_counter(update: Update, context: ContextTypes.DEFAULT_TYPE, counter_name):
    chat_id = update.effective_chat.id
    return context.bot_data.get(counter_name, {}).get(chat_id, 0)


def increment_arcana_counter(update: Update, context: ContextTypes.DEFAULT_TYPE, arcan):
    chat_id = update.effective_chat.id
    context.bot_data.setdefault("arcana_counter", {}).setdefault(
        chat_id, {}
    ).setdefault(arcan, 0)
    context.bot_data["arcana_counter"][chat_id][arcan] += 1


def get_arcana_stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    return context.bot_data.get("arcana_counter", {}).get(chat_id, {})


async def handle_get_stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    win = get_counter(update, context, "success_count")
    lose = get_counter(update, context, "failure_count")
    arcana_stat = get_arcana_stat(update, context)
    stat = "" if arcana_stat == {} else "Вот статистика по арканам:\n"
    text = f"""Я уже успешно распознал арканов: {win} \nНо было и несколько уродских сообщений: {lose} \n{stat}"""
    for arcan, count in arcana_stat.items():
        text += f"{arcan} аркан = {count}\n"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
    )


NOTIFICATION_CHAT_ID = "-4099609712"


async def notify_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE, message):
    user = update.message.from_user
    cursor = conn.cursor()
    # Выполняем запрос для подсчета количества пользователей
    cursor.execute("SELECT COUNT(id) FROM users")
    count = cursor.fetchone()[0]

    cursor = conn.cursor()

    # Обновляем запись пользователя в базе данных
    cursor.execute(
        "UPDATE users SET birth_date = ?, birth_date = ? WHERE chat_id = ?",
        (message, user.first_name, update.effective_chat.id),
    )
    conn.commit()

    notification_text = f"Новый пользователь: {user.first_name} (@{user.username} родился: {message})\n\nВсего пользователей на данный момент: {count}"
    # update.effective_chat.id

    await context.bot.send_message(chat_id=NOTIFICATION_CHAT_ID, text=notification_text)


async def notify_referal_program(
    update: Update, context: ContextTypes.DEFAULT_TYPE, refer
):
    user = update.message.from_user
    notification_text = f"Пользователя: {user.first_name} пригласил {refer})"
    await context.bot.send_message(chat_id=NOTIFICATION_CHAT_ID, text=notification_text)


async def notify_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # user = update.message.from_user
    notification_text = f"Полина молодец!\n\n Этому человеку все понравилось: {context.user_data['first_name']} (@{context.user_data['username']} родился: {context.user_data['real_birth_date']})\n Если интересно, то изначально он выбрал сферу: {context.user_data['choose']}. Теперь через недельку можем написать ему и надавить именно на эту сферу!!!"
    await context.bot.send_message(chat_id=NOTIFICATION_CHAT_ID, text=notification_text)


async def notify_julik(context: ContextTypes.DEFAULT_TYPE):
    # user = update.message.from_user
    notification_text = f"Этот грязный жулик хотел нас наебать и обнулить бота:\n\n {context.user_data['first_name']} (@{context.user_data['username']})\n"
    await context.bot.send_message(chat_id=NOTIFICATION_CHAT_ID, text=notification_text)


async def notify_no(update: Update, context: ContextTypes.DEFAULT_TYPE, feedback):
    # user = update.message.from_user
    feedback = f"вот на что жалуется:{feedback}" if feedback else ""
    notification_text = f"Ура с нами поделились честной обратной связью!\n\n Этой пидорасине что-то не понравилось: {context.user_data['first_name']} (@{context.user_data['username']} родился: {context.user_data['real_birth_date']})\n Если интересно(хотя похуй), то изначально он выбрал сферу: {context.user_data['choose']}. Теперь через недельку можем разбить ему ебало!!!\n\n{feedback}"
    await context.bot.send_message(chat_id=NOTIFICATION_CHAT_ID, text=notification_text)


# Функция для обработки нажатия на кнопку
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await query.edit_message_reply_markup(reply_markup=None)

    user = context.user_data["user"]
    query = update.callback_query
    await query.answer()

    if query.data == "0":
        context.user_data["choose"] = "Отношения"
    elif query.data == "1":
        context.user_data["choose"] = "Финансы"
    elif query.data == "2":
        context.user_data["choose"] = "Саморазвитие"
    else:
        context.user_data["choose"] = "Не знаю"
    # context.user_data["burn"] = "Финансы"
    # await query.edit_message_reply_markup(reply_markup=None)
    date_sum = sum(
        int(digit) for part in context.user_data["birth_date"] for digit in part
    )
    arcan = calculate_arcan(date_sum)
    context.user_data["arcan"] = arcan
    cursor.execute(
        "UPDATE users SET arcan = ? WHERE user_id = ?", (arcan, user.id))
    conn.commit()
    increment_arcana_counter(update, context, arcan)
    if not context.user_data["is_robot_sure"]:
        increment_counter(update, context, "success_count")
    else:
        increment_counter(update, context, "failure_count")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'{context.user_data["is_robot_sure"]}{user.first_name}, твой аркан: {arcan}',
    )
    await send_arcan(update, context, arcan, query.data)
    await context.bot.delete_message(
        chat_id=query.message.chat_id, message_id=query.message.message_id
    )

    # Задержка в 2 секунды
    await asyncio.sleep(2)

    # Создаем клавиатуру с кнопками
    keyboard = [
        [InlineKeyboardButton(
            "Понравился, хочу остальные сферы", callback_data="yes")],
        [InlineKeyboardButton("Нет, не понравился", callback_data="no")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с кнопками
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Буду благодарна обратной связи!\nПонравился ли тебе прогноз?",
        reply_markup=reply_markup,
    )

    # await query.edit_message_text(text=response)


async def handle_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await context.bot.delete_message(
        chat_id=query.message.chat_id, message_id=query.message.message_id
    )
    # Обработка ответа "Да"
    await notify_yes(update, context)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Отлично! Рада, что тебе понравилось❤️"
    )
    # context.user_data["user"].id
    await ask_to_invite_friend(update, context, context.user_data["user"])
    # await send_arcan(update, context, context.user_data["arcan"], None)


async def handle_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await notify_no(update, context, None)
    # Обработка ответа "Нет"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Cпасибо за обратную связь!\n\nЖаль, что тебе не понравилось. Я постараюсь улучшить свой продукт😢\n\nБуду признательна, если расскажешь, что именно тебе не понравилось?",
    )
    # Сохраняем состояние, что ожидаем обратную связь
    context.user_data["awaiting_feedback"] = True
    context.user_data["dataaa"] = query.message


async def feedback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # user = update.effective_user
    if context.user_data["was_met"] and context:
        return
    if context.user_data.get("awaiting_feedback"):
        feedback = update.message.text
        await notify_no(update, context, feedback)
        context.user_data["awaiting_feedback"] = False

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Спасибо за твою обратную связь!"
        )
    else:
        await handle_birthday(update, context)


async def handle_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update, context, "-1001909137196"):
        await ask_to_invite_friend(update, context, context.user_data["user"])
        return
    else:
        await send_arcan(update, context, context.user_data["arcan"], None)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    cursor = conn.cursor()

    # Получаем ID реферера из аргументов команды, если они есть
    referrer_id = int(context.args[0]) if context.args else None

    # Проверяем, задан ли username пользователя
    if user.username is not None:
        # Если username задан  ищем пользователя по username или user_id
        cursor.execute(
            "SELECT id FROM users WHERE username = ? OR user_id = ?",
            (user.username, user.id),
        )
    else:
        cursor.execute("SELECT id FROM users WHERE user_id = ?", (user.id,))

    user_record = cursor.fetchone()

    # Проверяем, существует ли пользователь в базе данных
    # cursor.execute(
    #     "SELECT id FROM users WHERE username = ? or user_id = ?",
    #     (
    #         user.username,
    #         user.id,
    #     ),
    # )
    # user_record = cursor.fetchone()
    if (
        user.username != "polinaataroo"
        and user.username != "willameh"
        and user_record is not None
    ):
        # Пользователь найден в базе данных
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Привет, {user.first_name}!\n\nБольшое спасибо за проявленный интерес к моей деятельности❤️\n\nМы уже знакомы, данным ботом можно воспользоваться только один раз 😢\n\nЕсли возникли вопросы -- напиши мне: @polinaataroo 💌",
        )
        await notify_julik(context)
        context.user_data["was_met"] = True
    else:
        # Пользователь не найден, добавляем его в базу данных
        cursor.execute(
            "INSERT INTO users (username, chat_id, user_id) VALUES (?, ?, ?)",
            (user.username, chat_id, user.id),
        )
        user_id = cursor.lastrowid
        conn.commit()

        # Регистрация реферера, если таковой есть
        if referrer_id:
            cursor.execute(
                "INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)",
                (referrer_id, user_id),
            )
            conn.commit()
            # Отправляем уведомление рефереру
            await notify_referrer(update, context, referrer_id, user.username)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Привет, {user.first_name}!\n\nБольшое спасибо за проявленный интерес к моей деятельности ❤️\n\nЯ дарю тебе небольшой разбор твоего аркана и личный прогноз на 2024 год.\nВыбирай с умом, доступна только одна сфера ✨\n\nНапиши, пожалуйста, свою дату рождения в формате ДД.MM.ГГГГ",
        )
        context.user_data["was_met"] = False

    context.user_data["first_name"] = user.first_name
    context.user_data["username"] = user.username


async def notify_referrer(
    update: Update, context: ContextTypes.DEFAULT_TYPE, referrer_id, new_user_username
):
    # Функция для отправки уведомления рефереру о новом пользователе
    cursor = conn.cursor()
    cursor.execute(
        "SELECT chat_id FROM users WHERE user_id = ?", (referrer_id,))
    if referrer_record := cursor.fetchone():
        referrer_chat_id = referrer_record[0]
        await context.bot.send_message(
            chat_id=referrer_chat_id,
            text=f"Твой друг @{new_user_username} зарегистрировался по твоей ссылке!",
        )
        cursor.execute(
            "SELECT arcan FROM users WHERE user_id = ?", (referrer_id,))
        result = cursor.fetchone()

        if not check_if_user_received_all_files(referrer_id) or referrer_id == 1358227914:
            await send_arcan(
                update, context, result[0] if result else None, None, referrer_chat_id
            )
            await context.bot.send_message(
                chat_id=referrer_chat_id,
                text=f"Если у тебя остались вопросы или ты хочешь глубже разобрать сферы своей жизни, то пиши мне в личные сообщения @polinaataroo\n💌\n\nТакже я дарю тебе скидку 20% на любую из моих услуг, промокод -- твой ник телеграм, предложение действует до {calculate_future_date(5)}❤️\n\nНе отписывайся от этого бота, тут будет польза по твоему Аркану ✨",
            )
    cursor.execute(
        "UPDATE users SET already_have_all_files = 'yes' WHERE user_id = ?",
        (referrer_id,),
    )
    conn.commit()
    # cursor1 = conn.cursor()
    cursor.execute(
        "SELECT username FROM users WHERE user_id = ?", (referrer_id,))
    res = cursor.fetchone()
    res = res[0] if res else None
    await notify_referal_program(update, context, res)


def calculate_future_date(days_ahead):
    """
    Функция для вычисления будущей даты, увеличенной на указанное количество дней.
    Формат даты: dd.mm.yy
    """
    current_date = datetime.now()
    future_date = current_date + timedelta(days=days_ahead)
    return future_date.strftime("%d.%m.%y")


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


def write_username_to_file(username, file_path):
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(username + "\n")


def check_username_in_file(username, file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            usernames = [line.strip() for line in file]
            return username in usernames
    except FileNotFoundError:
        return False


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), feedback_handler)
    )
    # Обработка сообщений с датой рождения
    application.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), handle_birthday)
    )
    application.add_handler(
        CallbackQueryHandler(confirm_birthday_button,
                             pattern="^confirm_date_(yes|no)$")
    )
    # Обработка статистики
    application.add_handler(CommandHandler("getStat", handle_get_stat))
    application.add_handler(CallbackQueryHandler(handle_yes, pattern="^yes$"))
    application.add_handler(CallbackQueryHandler(handle_no, pattern="^no$"))
    application.add_handler(
        CallbackQueryHandler(handle_subscribe, pattern="^subscribe$")
    )
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()
