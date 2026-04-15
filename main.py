# 6951072200
import asyncio
import logging
import os
from app.handlers import router
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from app.database.models import async_main
import app.config as config
from app.database.requests import load_blocked_users


async def main():
    await async_main()
    await load_blocked_users()
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'))  # token=os.getenv(TOKEN))
    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
