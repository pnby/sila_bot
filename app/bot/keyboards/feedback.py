from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.keyboards.general import back_to_main_button

feedback_buttons = [
    InlineKeyboardButton(text='1', callback_data='feedback_1'),
    InlineKeyboardButton(text='2', callback_data='feedback_2'),
    InlineKeyboardButton(text='3', callback_data='feedback_3'),
    InlineKeyboardButton(text='4', callback_data='feedback_4'),
    InlineKeyboardButton(text='5', callback_data='feedback_5')
]

feedback_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        feedback_buttons,
        [back_to_main_button]
    ]
)
