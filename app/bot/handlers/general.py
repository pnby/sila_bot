import asyncio
import time
from concurrent.futures.thread import ThreadPoolExecutor
from random import randrange

from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.bot import logger, bot
from app.bot.api.ollama.impl.ollama import Ollama
from app.bot.config import UPLOADS_DIR, user_prompt, system_prompt
from app.bot.handlers.staff import questions
from app.bot.keyboards.general import start_keyboard, answer_inline_keyboard, back_to_main_button
from app.bot.states.general import GeneralStates
from app.bot.utils.utils import extract_text_from_all_docx_files

router = Router()

@router.message(Command(commands=["start"]))
async def start_handler(message: Message, state: FSMContext):
    """
    Handles the /start command. Clears the state and sends a welcome message with the start keyboard.
    """
    await state.clear()
    await message.answer('Приветствую. Я виртуальный ассистент клиентской помощи ООО Сила.', reply_markup=start_keyboard)

@router.callback_query(F.data == "back_to_main_button")
async def back_to_main(callback_query: CallbackQuery):
    """
    Handles the 'back_to_main_button' callback query. Edits the message to return to the main menu.
    """
    await callback_query.message.edit_text(text="Приветствую. Я виртуальный ассистент клиентской помощи ООО Сила.", reply_markup=start_keyboard)


@router.callback_query(F.data == "support_button")
async def support_button_handler(callback_query: CallbackQuery, state: FSMContext):
    """
    Handles the 'support_button' callback query. Sets the state to GET_HELP and prompts the user to describe their problem.
    """
    await state.set_state(GeneralStates.GET_HELP)
    await callback_query.message.answer(text='Внятно объясните и изложите суть своей проблемы и/или вопроса.')


@router.message(GeneralStates.GET_HELP)
async def help_handler(message: Message, state: FSMContext):
    """
    Handles messages in the GET_HELP state. Processes text input and streams the response.
    """
    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        loop = asyncio.get_running_loop()

        with ThreadPoolExecutor() as executor:
            raw_text: str = await loop.run_in_executor(executor, extract_text_from_all_docx_files, UPLOADS_DIR)

        formatted_user_prompt = user_prompt(message.text)
        sys_prompt = system_prompt(raw_text)

        logger.debug(sys_prompt)

        ollama = Ollama(formatted_user_prompt, system_prompt=sys_prompt, stream=True)

        msg = await message.answer("Успешно!")
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        accumulated_text = ""
        last_update_time = time.time()

        async for chunk in ollama.stream_response():
            accumulated_text += chunk

            if time.time() - last_update_time >= float(randrange(2, 3)):
                await msg.edit_text(accumulated_text)
                await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
                last_update_time = time.time()

        await msg.edit_text(accumulated_text, reply_markup=answer_inline_keyboard)
        await state.clear()
    except Exception as e:
        await message.answer("Произошла неизвестная ошибка, обратитесь в поддержку")
        logger.warning(e)


@router.callback_query(F.data == "faq_button")
async def faq_button_handler(callback_query: CallbackQuery):
    """
    Handles the 'faq_button' callback query. Displays FAQ questions as inline buttons.
    """
    if not questions:
        logger.debug(questions)
        await callback_query.message.answer("Список FAQ пуст. Пожалуйста, обновите его.")
        return

    faq_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=question.title, callback_data=f"quest_{index}")]
            for index, question in enumerate(questions)
        ]
    )

    faq_keyboard.inline_keyboard.append([back_to_main_button])

    await callback_query.message.edit_text("Часто задаваемые вопросы:", reply_markup=faq_keyboard)

@router.callback_query(F.data.startswith("quest_"))
async def faq_answer_handler(callback_query: CallbackQuery):
    """
    Handles the FAQ question selection and shows the answer.
    """
    index = int(callback_query.data.split("_")[1])

    if index < len(questions):
        question = questions[index]
        await callback_query.message.edit_text(
            f"*{question.title}*\n\n{question.answer}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back_to_main_button]])
        )
    else:
        await callback_query.answer("Неверный индекс вопроса.", show_alert=True)

@router.callback_query(F.data == "guide_button")
async def guide_button_handler(callback_query: CallbackQuery):
    """
    Handles the 'guide_button' callback query. Edits the message to show the guide with a back button.
    """
    text = (
        "Это руководство по использованию бота:\n\n"
        "1. /start - Начало работы и сброс состояний.\n"
        "2. /admin - Админка\n"
    )
    back_keyboard = InlineKeyboardMarkup(text=text, inline_keyboard=[
        [back_to_main_button]
    ])
    await callback_query.message.edit_text(text=text, reply_markup=back_keyboard)