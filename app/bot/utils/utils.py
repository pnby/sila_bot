import os

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, File
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot import logger
from app.bot.config import UPLOADS_DIR


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

    return kb_builder.as_markup()


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