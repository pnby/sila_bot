import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, Document

from app.bot import logger, bot
from app.bot.api.ollama.impl.ollama import Ollama
from app.bot.config import UPLOADS_DIR, super_user_id
from app.bot.keyboards.staff import choice_keyboard, document_keyboard, back_to_document_management_keyboard
from app.bot.states.staff import StaffStates
from app.bot.utils.utils import delayed_message_delete, create_paginated_keyboard_from_directory, Question, \
    extract_text_from_all_docx_files

router = Router()

questions: List[Question] = []

@router.message(Command(commands=["admin"]))
async def define_post(message: Message):
    """
        Handles the /admin command.
    """
    if message.from_user.id != super_user_id:
        return

    await message.answer("Панель управления ботом открыта", reply_markup=choice_keyboard)

@router.callback_query(F.data == "list_document_button")
async def support_button_handler(callback_query: CallbackQuery):
    """
    Handles the 'list_document_button' callback query. Sends a list of uploaded documents.
    """
    if callback_query.from_user.id != super_user_id:
        return

    keyboard = create_paginated_keyboard_from_directory()
    await callback_query.message.edit_text(text="Список загруженных документов", reply_markup=keyboard)

@router.callback_query(F.data.startswith("document_management_button"))
async def open_document_panel(callback_query: CallbackQuery):
    """
    Handles the 'document_management_button' callback query. Opens the document management panel.
    """
    await callback_query.message.edit_text(text="Документная панель открыта", reply_markup=document_keyboard)

@router.callback_query(F.data == "back_to_choice")
async def back_to_choice(callback_query: CallbackQuery):
    """
    Handles the 'back_to_choice' callback query. Returns to the main menu.
    """
    await callback_query.message.edit_text(text="Вы вернулись в главное меню", reply_markup=choice_keyboard)

@router.callback_query(F.data == "back_to_choice_admin")
async def back_to_choice_admin(callback_query: CallbackQuery):
    """
    Handles the 'back_to_choice_admin' callback query. Returns to the main menu.
    """
    await callback_query.message.edit_text(text="Вы вернулись в главное меню", reply_markup=choice_keyboard)



if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

@router.callback_query(F.data.startswith("load_document_button"))
async def load_document(callback_query: CallbackQuery, state: FSMContext):
    """
    Handles the 'load_document_button' callback query. Prompts the user to upload a document.
    """
    if callback_query.from_user.id != super_user_id:
        return

    await callback_query.message.edit_text("Загрузите документ", reply_markup=back_to_document_management_keyboard)
    await state.set_state(StaffStates.LOAD_DOCUMENT)

async def handle_faq(ollama: Ollama, message: Message):
    await ollama.send_request()
    answer = ollama.get_formatted_response()

    try:
        data = json.loads(answer)
        logger.debug(data)
        for obj in data["questions"]:
            questions.append(Question(title=obj["title"], answer=obj["answer"]))

        await bot.send_message(message.chat.id, "Успешно!")
    except (json.JSONDecodeError, KeyError) as e:
        await message.answer("Ошибка при обработке данных FAQ.")
        logger.warning(f"Ошибка при загрузке FAQ: {e}")

    await bot.send_message(message.from_user.id, "Успешно!")


@router.callback_query(F.data == "faq_regeneration_button")
async def generate_faq(callback_query: CallbackQuery):
    if callback_query.from_user.id != super_user_id:
        return

    loop = asyncio.get_running_loop()

    with ThreadPoolExecutor() as executor:
        raw_text: str = await loop.run_in_executor(executor, extract_text_from_all_docx_files, UPLOADS_DIR)

    ollama = Ollama(f"""
    Тебе нужно придумать пять вопросов-ответов основываясь на базу знаний. Ответ должен быть ТОЛЬКО в формате JSON, без комментариев и прочего.
    <json-schema>
    {{
      "questions": [
        {{
          "title": "string",
          "answer": "string"
        }}
      ]
    }}
    </json-schema>
    База знаний: {raw_text}
    """, jsonify=True)
    await callback_query.message.answer("Генерация займет много времени...")
    await asyncio.create_task(handle_faq(ollama, callback_query.message))

@router.message(StaffStates.LOAD_DOCUMENT)
async def handle_document(message: Message, state: FSMContext):
    """
    Handles document uploads in the LOAD_DOCUMENT state. Saves the document to the uploads directory.
    """

    document: Optional[Document] = message.document
    if document is None:
        message = await message.answer("Загрузите валидный документ")
        await delayed_message_delete(message)
        return

    file_id = document.file_id
    file = await message.bot.get_file(file_id)
    file_path = file.file_path

    destination = os.path.join(UPLOADS_DIR, document.file_name)
    await message.bot.download_file(file_path, destination)

    message = await message.answer(f"Документ {document.file_name} загружен")
    await state.clear()
    await delayed_message_delete(message)

@router.callback_query(F.data.startswith("unload_document_button"))
async def unload_document(callback_query: CallbackQuery, state: FSMContext):
    """
    Handles the 'unload_document_button' callback query. Prompts the user to enter the filename to delete.
    """
    if callback_query.from_user.id != super_user_id:
        return

    await callback_query.message.edit_text("Введите имя файла для удаления", reply_markup=back_to_document_management_keyboard)
    await state.set_state(StaffStates.UNLOAD_DOCUMENT)

@router.message(StaffStates.UNLOAD_DOCUMENT)
async def handle_unload_document(message: Message, state: FSMContext):
    """
    Handles document deletion in the UNLOAD_DOCUMENT state. Deletes the specified file from the uploads directory.
    """
    file_name = message.text
    file_path = os.path.join(UPLOADS_DIR, file_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        message = await message.answer(f"Файл {file_name} удален")
        await delayed_message_delete(message)
    else:
        await message.answer(f"Файл {file_name} не найден")
        await delayed_message_delete(message)

    await state.clear()