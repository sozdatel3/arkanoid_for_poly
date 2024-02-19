from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def hello(name):
    return f"Привет, {name}!\n\nБольшое спасибо за проявленный интерес к моей деятельности❤️\n\nМы уже знакомы, данным ботом можно воспользоваться только один раз 😢\n\nЕсли возникли вопросы -- напиши мне: @polinaataroo 💌"


def hello_good(name):
    return f"Привет, {name}!\n\nБольшое спасибо за проявленный интерес к моей деятельности ❤️\n\nЯ дарю тебе небольшой разбор твоего аркана и личный прогноз на 2024 год.\nВыбирай с умом, доступна только одна сфера ✨\n\nНапиши, пожалуйста, свою дату рождения в формате ДД.MM.ГГГГ"


def ask_to_send_friend(referral_link):
    return f"Я уже рассказала тебе про одну сферу.\nЕсли интересны остальные -- отправь другу эту ссылку:\n\n{referral_link} \n\nи как только он зарегистрируется, я отправлю тебе оставшиеся материалы ✨"


def is_it_correct_date(date):
    return f"Так как у вас всего одна попытка, проверьте свою дату рождения. Всё верно?\nВаша дата: {date}"


no_good_date = "Хорошо, пожалуйста, отправьте мне корректную дату рождения🙏🏼"

not_shure = "Я не уверен и скорее всего ошибаюсь, но возможно это правильный аркан, лучше проверь: "

glad_to_feedback = "Буду благодарна обратной связи!\nПонравился ли тебе прогноз?"
bad_feedback = "Cпасибо за обратную связь!\n\nЖаль, что тебе не понравилось. Я постараюсь улучшить свой продукт😢\n\nБуду признательна, если расскажешь, что именно тебе не понравилось?"
keybord_like = [
    [InlineKeyboardButton(
        "Понравился, хочу остальные сферы", callback_data="yes")],
    [InlineKeyboardButton("Нет, не понравился", callback_data="no")],
]

keyboard_sphere = [
    [InlineKeyboardButton("Отношения❤️", callback_data="0")],
    [InlineKeyboardButton("Финансы💸", callback_data="1")],
    [InlineKeyboardButton("Саморазвитие📚", callback_data="2")],
]

keyboard_yes_no = [
    [InlineKeyboardButton("Да", callback_data="confirm_date_yes")],
    [InlineKeyboardButton("Нет", callback_data="confirm_date_no")],
]
