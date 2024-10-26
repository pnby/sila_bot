import asyncio
import time
from concurrent.futures.thread import ThreadPoolExecutor
from random import randrange

from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.bot import logger, bot
from app.bot.api.ollama.impl.ollama import Ollama
from app.bot.config import UPLOADS_DIR, user_prompt, system_prompt
from app.bot.keyboards.general import start_keyboard, answer_inline_keyboard
from app.bot.states.general import GeneralStates
from app.bot.utils.utils import extract_text_from_all_docx_files

router = Router()

@router.message(Command(commands=["start"]))
async def start_handler(message: Message, state: FSMContext):
    """
    Handles the /start command. Clears the state and sends a welcome message with the start keyboard.
    """
    await state.clear()
    await message.answer('Приветствую. Я ассистент для клиентов ООО Сила, для получения полной справки обо мне напишите /help', reply_markup=start_keyboard)



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