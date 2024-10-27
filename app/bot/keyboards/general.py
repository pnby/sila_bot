from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

back_to_main_button = InlineKeyboardButton(text="Назад", callback_data="back_to_main_button")

faq_button = InlineKeyboardButton(text='FAQ', callback_data='faq_button')
guide_button = InlineKeyboardButton(text='Руководство', callback_data='guide_button')
support_button = InlineKeyboardButton(text='Поддержка', callback_data='support_button')
feedback_button = InlineKeyboardButton(text='Оставить фидбек', callback_data='feedback_button')

start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [faq_button, support_button],
        [guide_button],
        [feedback_button]
    ]
)

repeat_request_to_ai = InlineKeyboardButton(text="Спросить AI снова", callback_data="support_button")

#
# In the message when the neural network responds to the user
#
answer_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [repeat_request_to_ai],
])