from xmlrpc.client import Boolean
from telegram.error import TelegramError
from telegram import Bot
from march import *
import asyncio
import os
from telegram.ext import (
    # Updater,
    MessageHandler,
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)
from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from dateparser.search.search import DateSearchWithDetection
from telegram import InputFile
from march import *
from db import check_if_user_received_one_file, cursor, conn, set_already_recive_all_march, set_already_recive_one, set_birth_date, what_choose_in_march
from all_text import (
    hello,
    ask_to_send_friend,
    is_it_correct_date,
    no_good_date,
    not_shure,
    keybord_like,
    glad_to_feedback,
    keyboard_sphere,
    keyboard_yes_no,
    hello_good,
    bad_feedback
)
from help import *
from notify import *

TOKEN = os.getenv("TOKEN")


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
    # print(f"BIRTH DATE ={birth_date}")
    return birth_date


async def ask_to_invite_friend(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user
):
    user_id = update.effective_user.id
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text=ask_to_send_friend(referral_link),
        # reply_markup=reply_markup,
    )


async def handle_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    # if context.user_data.get("was_met") and check_if_user_received_one_file(update.effective_user.id):
    if check_if_user_received_one_file(update.effective_user.id) and update.effective_user.id != 1358227914 and update.effective_user.id != 740905109:
        return
    message = update.message.text
    # Сохраняем дату в user_data
    context.user_data["temporary_birth_date"] = message
    # Сохраняем дату в user_data
    context.user_data["temporary_update"] = update
    context.user_data["temporary_user"] = user  # Сохраняем дату в user_data
    # context.user_data["temporary_contex"] = update  # Сохраняем дату в user_data

    # Создаем клавиатуру для подтверждения даты рождения
    reply_markup = InlineKeyboardMarkup(keyboard_yes_no)

    await update.message.reply_text(
        text=is_it_correct_date(message),
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
            text=no_good_date,
        )
        user_data["awaiting_new_birth_date"] = True
    elif query.data == "confirm_date_yes":
        await context.bot.delete_message(
            chat_id=query.message.chat_id, message_id=query.message.message_id
        )
        context.user_data["was_met"] = True
        set_already_recive_one(query.message.chat_id)
        # Получаем сохраненную дату
        message = user_data.get("temporary_birth_date")
        set_birth_date(query.message.chat_id, message)

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
            ] = not_shure
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

        reply_markup = InlineKeyboardMarkup(keyboard_sphere)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Пожалуйста, выберите один из вариантов:",
            reply_markup=reply_markup,
        )


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


# Функция для обработки нажатия на кнопку
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await query.edit_message_reply_markup(reply_markup=None)
    user = context.user_data["user"]
    query = update.callback_query
    await query.answer()

    # print(f"QDATA={query.data}")
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

    reply_markup = InlineKeyboardMarkup(keybord_like)

    # Отправляем сообщение с кнопками
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=glad_to_feedback,
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
        text=bad_feedback,
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
    extra = False
    referrer_id = None
    # Получаем ID реферера из аргументов команды, если они есть
    # print("TUUUT")
    # print(context.args[0].split("_"))
    try:
        if context.args:
            params = context.args[0].split('_')
    
    # referrer_id = int(context.args[0]) if context.args else None
            referrer_id = int(params[0]) if context.args else None
            extra = Boolean(params[1]) if params[1] else None
        else:
            referrer_id =  None
            extra =  None
            
    except:
        pass
        # params = None
        # referrer_id = None
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
    # print(f"EXTRA = {extra}")
    if (
        user.username != "polinaataroo"
        and user.username != "willameh"
        and user_record is not None
        and check_if_user_received_one_file(update.effective_user.id)
    ):
        # Пользователь найден в базе данных
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=hello(user.first_name),
        )
        await notify_julik(context)
        context.user_data["was_met"] = True
    else:
        # Пользователь не найден, добавляем его в базу данных
        cursor.execute(
            "INSERT INTO users (username, chat_id, user_id, first_meet) VALUES (?, ?, ?, ?)",
            (user.username, chat_id, user.id, datetime.now()),
        )
        user_id = cursor.lastrowid
        conn.commit()

        # Регистрация реферера, если таковой есть
        if referrer_id and not extra:
            cursor.execute(
                "INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)",
                (referrer_id, user_id),
            )
            conn.commit()
            # Отправляем уведомление рефереру
            await notify_referrer(update, context, referrer_id, user.username)
        if extra:
            set_already_recive_all_march(referrer_id)
            # send_all_march(update, context, referrer_id)
            choice_march = what_choose_in_march(int(referrer_id))
            await send_march_file(update, context, int(referrer_id), choice_march, TRUE)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=hello_good(user.first_name),
        )
        context.user_data["was_met"] = False

    context.user_data["first_name"] = user.first_name
    context.user_data["username"] = user.username


async def send_file_to_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ids = cursor.execute(
        "SELECT chat_id FROM users WHERE file_sent = TRUE").fetchall()
    for chat_id, in chat_ids:
        arcan = cursor.execute(
            "SELECT arcan FROM users WHERE chat_id = ?", (chat_id,)).fetchone()
        if arcan:
            try:
                with open(f'../misk/02/{arcan[0]}.pdf', "rb") as pdf_file:
                    await context.bot.send_document(
                        chat_id=chat_id,
                        document=InputFile(
                            pdf_file, filename=f"{arcan[0]}.pdf"),
                        caption="Спасибо, что не отписалась/ся 🤍\n\nЯ ценю твою поддержку.\n\nДержи новый файл с полезной информацией по твоему Аркану",
                    )
                    cursor.execute(
                        "UPDATE users SET file_sent = TRUE WHERE chat_id = ?", (chat_id,))
                    conn.commit()
                # Отправляем вопрос после успешной отправки файла
                await send_feedback_question(context.bot, chat_id)
            except TelegramError as e:
                print(f"Не удалось отправить файл пользователю {chat_id}: {e}")
                cursor.execute(
                    "UPDATE users SET file_sent = FALSE WHERE chat_id = ?", (chat_id,))
                conn.commit()


async def send_feedback_question(bot, chat_id):
    question_text = "Помоги мне улучшить свой продукт🤍\n\nЯ забочусь о твоем комфорте, поэтому мне важно понять, как часто тебе комфортно получать полезную информацию от этого бота?✨"
    keyboard = [
        [InlineKeyboardButton("1 раз в месяц", callback_data='1_per_month')],
        [InlineKeyboardButton("2 раза в месяц", callback_data='2_per_month')],
        [InlineKeyboardButton("3 раза в месяц", callback_data='3_per_month')],
        [InlineKeyboardButton("Никогда", callback_data='never')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id, question_text, reply_markup=reply_markup)


async def feedback_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data  # Получаем данные от callback_data
    user_id = query.from_user.id

    # Записываем выбор пользователя в базу данных
    cursor.execute(
        "UPDATE users SET feedback_choice = ? WHERE chat_id = ?", (choice, user_id))
    conn.commit()

    thank_you_text = "Благодарю тебя🤍\n\nЕсли остались дополнительные вопросы -- можешь писать мне в личные сообщения @polinaataroo\n\nТакже знай, что ты всегда можешь изменить свой выбор о частоте получаемых сообщений🤍"
    await context.bot.send_message(chat_id=user_id, text=thank_you_text)

async def get_statistic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_user.id
    if update.effective_user.id == 1358227914 or update.effective_user.id == 740905109:
        with open(make_excel_file('../stat/'), "rb") as stat_file:
                    await context.bot.send_document(
                        chat_id=chat,
                        document=InputFile(
                            stat_file),
                        caption="Спасибо, что пользуетесь кодом Ярослава 🤍\n\nЯ ценю твою поддержку.\n\nДержи новый файл с полезной информацией🤍",
                    )

async def send_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверка прав пользователя перед отправкой файла всем пользователям
    # ADMIN_ID - ваш Telegram ID для проверки
    if update.effective_user.id == 1358227914 or update.effective_user.id == 740905109:
        await send_file_to_all_users(update, context)
        await update.message.reply_text("Файлы отправлены всем пользователям.")
    else:
        await update.message.reply_text("У вас нет прав для выполнения этой операции.")


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sendfile", send_file_command))
    application.add_handler(CommandHandler("sendMarch", march_send))
    application.add_handler(CommandHandler("getStat", get_statistic))
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
    pattern = "^(1_per_month|2_per_month|3_per_month|never)$"
    pattern_march = "^(relation|money|work)$"
    # pattern_for_first_choose = "^(0|1|2)$"
    application.add_handler(CallbackQueryHandler(
        feedback_callback_handler, pattern=pattern))
    application.add_handler(CallbackQueryHandler(handle_yes, pattern="^yes$"))
    application.add_handler(CallbackQueryHandler(handle_no, pattern="^no$"))
    # application.add_handler(CallbackQueryHandler(button, pattern=pattern_for_first_choose))
    application.add_handler(CallbackQueryHandler(
        choose_march_sphere, pattern=pattern_march))
    application.add_handler(CallbackQueryHandler(
        no_friend, pattern="^no_friend$"))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(
        CallbackQueryHandler(handle_subscribe, pattern="^subscribe$")
    )
    application.run_polling()


async def send_arcan(
    update: Update, context: ContextTypes.DEFAULT_TYPE, arcan, type, refer=None
):
    if not type:
        all_pdf = generate_pdf_path(arcan, 0, None)
        # print(f"SEND_all :{all_pdf}")
        for pdf in all_pdf:
            # print(f"TRY TO SEND_all :{pdf}")
            with open(pdf, "rb") as pdf_file:
                new_filename = clean_filename(os.path.basename(pdf))
                await context.bot.send_document(
                    chat_id=refer,
                    document=InputFile(pdf_file, filename=new_filename),
                    caption="",
                )
    else:
        # print(f"SEND :{all_pdf}")
        for i in range(3):
            # print(f"SEND :{pdf_path}")
            # print(arcan)
            # print(i)
            # print(type)
            if pdf_path := generate_pdf_path(arcan, i, type):
                with open(pdf_path, "rb") as pdf_file:
                    # print(f"TRY TO SEND :{pdf_path}")
                    new_filename = clean_filename(os.path.basename(pdf_path))
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=InputFile(pdf_file, filename=new_filename),
                        caption="",
                    )
