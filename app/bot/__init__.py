import logging

import torch
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.config import BOT_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
cuda_available = torch.cuda.is_available()

torch.device("cuda" if cuda_available else "cpu")
if not cuda_available:
    logger.warning("Cuda cores are unavailable, switching to CPU")