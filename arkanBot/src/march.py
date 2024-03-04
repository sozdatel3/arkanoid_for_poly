from pickle import TRUE
from telegram.error import TelegramError
from telegram import Bot
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

from db import check_if_user_received_one_file, cursor, conn, db_no_friend, get_nik, set_already_recive_one, set_birth_date
from all_text import *
from help import *
from notify import *

async def march_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == 1358227914 or update.effective_user.id == 740905109:
        #TODO
        chat_ids = cursor.execute(
            "SELECT chat_id FROM users WHERE march_send = FALSE").fetchall()
        #TODO
        await ask_all_users_which_sphere(update, context, chat_ids)
        # await send_march_file_to_all_users(update, context, chat_ids)
        await update.message.reply_text("Файлы отправлены всем пользователям.")
    else:
        await update.message.reply_text("У вас нет прав для выполнения этой операции.")
    

async def ask_all_users_which_sphere(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_ids):
    for chat_id, in chat_ids:
        try:
            reply_markup = InlineKeyboardMarkup(keyboard_sphere_march)
            await context.bot.send_message(
                chat_id=chat_id,
                # text="Привет, я приготовила для тебя личный прогноз на март, но немного опоздала\nКакая сфера тебя интересует?",
                text=hi_march,
                reply_markup = reply_markup
            )
            cursor.execute(
                "UPDATE users SET march_send = ? WHERE chat_id = ?", (TRUE, chat_id)).fetchall()
            conn.commit()
        except:
            pass
    # pass

async def choose_march_sphere(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # print("ТУТ")
    # print(update)
    # print(context)
    query = update.callback_query
    await query.answer()
    await context.bot.delete_message(
        chat_id=query.message.chat_id, message_id=query.message.message_id
    )
    choice_march = query.data
    user_id = query.from_user.id
    all_choice = {'relation': 'отношения', 'money': 'финансы','work': 'карьера'}
    choice_march = all_choice[choice_march]
    # Записываем выбор пользователя в базу данных
    cursor.execute(
        "UPDATE users SET march_sphere_chosen = ? WHERE chat_id = ?", (choice_march, user_id))
    conn.commit()
    await send_march_file(update, context, user_id, choice_march)
      
async def send_march_file(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id, choice_march, all=False):
    arcan = cursor.execute(
        "SELECT arcan FROM users WHERE chat_id = ?", (user_id,)).fetchone()
    if all:
        # choice_march =cursor.execute("SELECT march_sphere_chosen FROM users WHERE chat_id = ?", (user_id,)).fetchone()
        # print(f"CHOOSE = {choice_march}")
        all_choice = {'отношения' : 1,'финансы' : 1,'карьера': 1}
        all_choice[choice_march[0]] = 0
        for no_choice in all_choice:
            # print(f"ALL CHOOSE = {all_choice[no_choice]}")
            if all_choice[no_choice] == 1:
                await send_march_info(arcan, no_choice, context, user_id, "")
        await send_gift(update, context, user_id)
    else:
        # caption="Спасибо,за твою энергию 🤍\n\nЯ ценю твою поддержку.\n\nЭто твой прогноз на март, если понравилось - сделаю это регулярной рубрикой"
        caption=energy
        await send_march_info(arcan, choice_march, context, user_id, caption)

async def no_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    choice_march = cursor.execute("SELECT march_sphere_chosen FROM users WHERE chat_id = ?", (user_id,)).fetchone()
    db_no_friend(user_id)
    await send_march_file(update, context, user_id, choice_march, TRUE)
    
async def send_gift(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    image_path = '../misk/march/Gift.png'
    with open(image_path, "rb") as gift:
        caption = (f"Спасибо, что остаешься со мной! Я хочу отблагодарить тебя подарком\n\nЧтобы воспользоваться сертификатом, перешли это сообщение @polinaataroo 💌\n\nВот твой уникальный номер: {user_id}")
        gift_date = datetime.now().strftime("%d.%m.%Y")
        cursor.execute(
            "INSERT INTO gifts (user_id, already_take, gift_date) VALUES (?, ?, ?)",
            (user_id, "TRUE", gift_date),
        )
        conn.commit()
        await notify_gift(context, get_nik(user_id), user_id)
        await context.bot.send_photo(
            chat_id=user_id,
            photo=InputFile(gift),
            caption=caption,
        )

    
async def send_march_info(arcan, choice_march, context, user_id, caption):
    try:
        with open(f'../misk/march/{arcan[0]}_{choice_march}.pdf', "rb") as pdf_file:
            await context.bot.send_document(
                chat_id=user_id,
                document=InputFile(
                    pdf_file, filename=f"{choice_march}.pdf"),
                caption=caption,
            )
            cursor.execute(
                "UPDATE users SET march_send = TRUE WHERE chat_id = ?", (user_id,))
            conn.commit()
        if caption:
            await send_friend_ask(context.bot, user_id, context)
    except TelegramError as e:
        print(f"Не удалось отправить файл пользователю {user_id}: {e}")
        cursor.execute(
            "UPDATE users SET file_sent = FALSE WHERE chat_id = ?", (user_id,))
        conn.commit()

async def send_friend_ask(bot, user_id, context: ContextTypes.DEFAULT_TYPE,):
    # referral_link = f"https://t.me/polyArcanDevelopBot?start={user_id}_true"
    referral_link = f"https://t.me/PolyArkanBot?start={user_id}_true"
    chat_id = user_id
    reply_markup = InlineKeyboardMarkup(keyboard_no_friend)
    await context.bot.send_message(
        chat_id=chat_id,
        text=ask_to_send_friend_march(referral_link),
        reply_markup=reply_markup,
    )
    
# async def send_all_march(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id)
async def send_march_file_to_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_ids):
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
                        caption="Спасибо, что не отписалась/ся 🤍\n\nЯ ценю твою поддержку!\n\nДержи новый файл с полезной информацией по твоему Аркану",
                    )
                    cursor.execute(
                        "UPDATE users SET file_sent = TRUE WHERE chat_id = ?", (chat_id,))
                    conn.commit()
                # Отправляем вопрос после успешной отправки файла
                # await send_feedback_question(context.bot, chat_id)
            except TelegramError as e:
                print(f"Не удалось отправить файл пользователю {chat_id}: {e}")
                cursor.execute(
                    "UPDATE users SET file_sent = FALSE WHERE chat_id = ?", (chat_id,))
                conn.commit()
