from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [["/test", "/result", "/help"]],
        resize_keyboard=True
    )

def get_question_keyboard(options):
    keyboard = []
    for i, option in enumerate(options):
        keyboard.append([InlineKeyboardButton(option, callback_data=str(i))])
    return InlineKeyboardMarkup(keyboard)