import os
from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, Document

from app.bot.api.rag.impl.rag import load_documents
from app.bot.config import UPLOADS_DIR
from app.bot.keyboards.staff import choice_keyboard
from app.bot.states.staff import StaffStates

router = Router()

@router.message(Command(commands=["admin"]))
async def define_post(message: Message):
    """
        Handles the /admin command.
    """

    await message.answer("Меню открыто", reply_markup=choice_keyboard)

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
    await callback_query.message.answer("Загрузите документ")
    await state.set_state(StaffStates.LOAD_DOCUMENT)

@router.message(StaffStates.LOAD_DOCUMENT)
async def handle_document(message: Message, state: FSMContext):
    """
    Handles document uploads in the LOAD_DOCUMENT state. Saves the document to the uploads directory.
    """

    document: Optional[Document] = message.document
    if document is None:
        await message.answer("Загрузите валидный документ")
        return

    file_id = document.file_id
    file = await message.bot.get_file(file_id)
    file_path = file.file_path

    destination = os.path.join(UPLOADS_DIR, document.file_name)
    await message.bot.download_file(file_path, destination)

    await message.answer(f"Документ {document.file_name} загружен")
    await state.clear()
    load_documents()

@router.callback_query(F.data.startswith("unload_document_button"))
async def unload_document(callback_query: CallbackQuery, state: FSMContext):
    """
    Handles the 'unload_document_button' callback query. Prompts the user to enter the filename to delete.
    """
    await callback_query.message.answer("Введите имя файла для удаления")
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
        await message.answer(f"Файл {file_name} удален")
        load_documents()
    else:
        await message.answer(f"Файл {file_name} не найден")

    await state.clear()