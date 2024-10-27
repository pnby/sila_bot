from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

back_to_document_management_button = InlineKeyboardButton(text="Назад", callback_data="document_management_button")

back_to_document_management_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [back_to_document_management_button]
    ]
)

document_management_button = InlineKeyboardButton(text="Документная панель", callback_data="document_management_button")
faq_regeneration_button = InlineKeyboardButton(text="Регенерация FAQ", callback_data="faq_regeneration_button")

#
# Used to select keyboards
#
choice_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [document_management_button],
        [faq_regeneration_button]
    ]
)

load_document_button = InlineKeyboardButton(text="Загрузить документ", callback_data="load_document_button")
list_document_button = InlineKeyboardButton(text="Список документов", callback_data="list_document_button")
unload_document_button = InlineKeyboardButton(text="Выгрузить документ", callback_data="unload_document_button")
back_to_choice_button = InlineKeyboardButton(text="Назад", callback_data="back_to_choice")


#
# Used for document management
#
document_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [load_document_button, unload_document_button],
        [list_document_button],
        [back_to_choice_button]
    ]
)