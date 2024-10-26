import asyncio
import os
from functools import cache

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, File, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from docx import Document

from app.bot import logger
from app.bot.config import UPLOADS_DIR
from app.bot.keyboards.staff import back_to_document_management_button


def create_paginated_keyboard_from_directory(directory: str = UPLOADS_DIR, page: int = 1, items_per_page: int = 5) -> InlineKeyboardMarkup:
    """
    Creating dynamic keyboards
    :param directory:
    :param page:
    :param items_per_page:
    :return:
    """
    kb_builder = InlineKeyboardBuilder()

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_page_items = files[start_idx:end_idx]

    for i in range(0, len(current_page_items), 3):
        row = current_page_items[i:i + 3]
        kb_builder.row(*[InlineKeyboardButton(text=item, callback_data=f"file:{item}") for item in row])

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"page:{page - 1}"))
    if end_idx < len(files):
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"page:{page + 1}"))

    if nav_buttons:
        kb_builder.row(*nav_buttons)

    kb_builder.row(back_to_document_management_button)

    keyboard = kb_builder.as_markup()
    return keyboard

@cache
def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts all text from a DOCX file.

    :param file_path: Path to the DOCX file.
    :return: Text from the DOCX file as a string.
    """
    doc = Document(file_path)
    full_text = []

    for para in doc.paragraphs:
        full_text.append(para.text)

    return '\n'.join(full_text)

def extract_text_from_all_docx_files(directory: str) -> str:
    """
    Extracts text from all DOCX files in the specified directory.

    :param directory: Path to the directory.
    :return: A dictionary where the keys are the file names and the values are the extracted text.
    """
    string = ""

    for filename in os.listdir(directory):
        if filename.endswith('.docx'):
            file_path = os.path.join(directory, filename)
            text = extract_text_from_docx(file_path)
            logger.debug(text)
            string += text

    return string

async def delayed_message_delete(message: Message, timeout: int = 4):
    """

    :param message: Just aiogram message object
    :param timeout: The time after which the message will be deleted
    """
    await asyncio.sleep(timeout)
    await message.delete()

async def safe_download(file: File) -> str:
    """
    Secure downloading of voice message files
    :param file:
    :return:
    """
    logger.debug(f"Установка файла {file.file_id}")
    directory = UPLOADS_DIR

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, file.file_path.split("/")[-1])
    logger.debug(f"Путь {file_path}")

    await file.bot.download_file(file.file_path, destination=file_path)
    return file_path


def clean_text(text: str) -> str:
    """
    Clean the text by removing unwanted characters.

    Args:
        text (str): The input text.

    Returns:
        str: The cleaned text.
    """
    return text.replace('\n', ' ').replace('\t', ' ').strip()