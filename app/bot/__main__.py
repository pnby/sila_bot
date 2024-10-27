import asyncio

from aiogram import Dispatcher
from app.bot.utils.singleton import singleton

from app.bot.handlers.staff import router as staff_router
from app.bot.handlers.general import router as general_router
from app.bot.handlers.feedback import router as feedback_router


@singleton
class Startup:
    _dp = Dispatcher()

    async def start_polling(self):
        from app.bot import bot
        await self._dp.start_polling(bot)


    def register_routes(self):
        self._dp.include_routers(*[general_router, staff_router, feedback_router])


if __name__ == "__main__":
    startup = Startup()
    startup.register_routes()
    asyncio.run(startup.start_polling())