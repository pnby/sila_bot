from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.keyboards.feedback import feedback_keyboard
from app.bot.keyboards.general import start_keyboard

router = Router()

users = set()

@router.callback_query(F.data == "feedback_button")
async def feedback_button_handler(callback_query: CallbackQuery):
    """
    Handles the 'feedback_button' callback query. Edits the message to show the feedback keyboard.
    """
    telegram_id = callback_query.from_user.id

    if telegram_id in users:
        text = "Вы уже оставляли фидбек. Спасибо!"
        await callback_query.message.edit_text(text=text, reply_markup=start_keyboard)
    else:
        text = "Пожалуйста, оцените наш бот от 1 до 5:"
        users.add(telegram_id)
        await callback_query.message.edit_text(text=text, reply_markup=feedback_keyboard)


@router.callback_query(F.data.startswith("feedback_"))
async def handle_feedback(callback_query: CallbackQuery):
    """
    Handles the feedback callback query. Processes the feedback and returns to the main menu.
    """
    telegram_id = callback_query.from_user.id
    text = "Спасибо за ваш фидбек! Ваше мнение очень важно для нас."

    if telegram_id in users:
        await callback_query.message.edit_text(text=text, reply_markup=start_keyboard)
    else:
        users.add(telegram_id)
        await callback_query.message.edit_text(text=text, reply_markup=start_keyboard)