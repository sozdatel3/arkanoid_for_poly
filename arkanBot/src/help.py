import dateparser
import re
from datetime import datetime, timedelta
from glob import glob
import os
from telegram import Update
import logging

#
from dotenv import load_dotenv
from telegram.ext import (
    # Updater,
    MessageHandler,
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)


load_dotenv()

TOKEN = os.getenv("TOKEN")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


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


def calculate_future_date(days_ahead):
    """
    Функция для вычисления будущей даты, увеличенной на указанное количество дней.
    Формат даты: dd.mm.yy
    """
    current_date = datetime.now()
    future_date = current_date + timedelta(days=days_ahead)
    return future_date.strftime("%d.%m.%y")


# https://t.me/polinabelyaewa
def increment_counter(
    update: Update, context: ContextTypes.DEFAULT_TYPE, counter_name: str
):
    chat_id = update.effective_chat.id
    context.bot_data.setdefault(counter_name, {}).setdefault(chat_id, 0)
    context.bot_data[counter_name][chat_id] += 1


def replace_shit_from_string(str: str):
    return (
        str.replace("-", "")
        .replace(" ", "")
        .replace(":", "")
        .replace("0", "")
        .replace(",", "")
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


def get_counter(update: Update, context: ContextTypes.DEFAULT_TYPE, counter_name):
    chat_id = update.effective_chat.id
    return context.bot_data.get(counter_name, {}).get(chat_id, 0)


def increment_arcana_counter(update: Update, context: ContextTypes.DEFAULT_TYPE, arcan):
    chat_id = update.effective_chat.id
    context.bot_data.setdefault("arcana_counter", {}).setdefault(
        chat_id, {}
    ).setdefault(arcan, 0)
    context.bot_data["arcana_counter"][chat_id][arcan] += 1


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
