import asyncio

from aiogram import Dispatcher
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.bot.config import MONGO_URI
from app.bot.utils.singleton import singleton

from app.bot.handlers.staff import router as staff_router
from app.bot.handlers.general import router as general_router


@singleton
class Startup:
    _dp = Dispatcher()

    @staticmethod
    async def _init_database():
        client = AsyncIOMotorClient(MONGO_URI)
        await init_beanie(database=client.db_name, document_models=[])

    async def start_polling(self):
        from app.bot import bot
        await self._dp.start_polling(bot)


    def register_routes(self):
        self._dp.include_routers(*[general_router, staff_router])


if __name__ == "__main__":
    startup = Startup()
    startup.register_routes()
    asyncio.run(startup.start_polling())