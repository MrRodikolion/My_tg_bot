import asyncio
import logging

from aiogram import Bot, Dispatcher

from database import db
from handlers import client, admin

logging.basicConfig(level=logging.INFO)

bot = Bot(token="6420088892:AAGEUuE7tCMyQ-DaZSMQQBXCd_P5avuQe-Y")
dp = Dispatcher()
dp.include_routers(client.client_router, admin.admin_router)


async def main():
    await db.create_connection()

    # await admin.set_admin_commands(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
