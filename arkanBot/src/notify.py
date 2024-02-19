# from telegram.ext import (
#     # Updater,
#     MessageHandler,
#     filters,
#     ApplicationBuilder,
#     ContextTypes,
#     CommandHandler,
# )
from telegram.ext import (
    ContextTypes,
)
from telegram import Update
from db import conn, check_if_user_received_all_files, set_discount_end

from main import send_arcan
from help import calculate_future_date

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

        if (
            not check_if_user_received_all_files(referrer_id)
            or referrer_id == 1358227914
        ):
            await send_arcan(
                update, context, result[0] if result else None, None, referrer_chat_id
            )
            await context.bot.send_message(
                chat_id=referrer_chat_id,
                text=f"Если у тебя остались вопросы или ты хочешь глубже разобрать сферы своей жизни, то пиши мне в личные сообщения @polinaataroo\n💌\n\nТакже я дарю тебе скидку 20% на любую из моих услуг, промокод -- твой ник телеграм, предложение действует до {calculate_future_date(5)}❤️\n\nНе отписывайся от этого бота, тут будет польза по твоему Аркану ✨",
            )
            set_discount_end(referrer_chat_id, calculate_future_date(5))

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
