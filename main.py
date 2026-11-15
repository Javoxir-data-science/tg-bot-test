# -*- coding: utf-8 -*-
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database.db import init_db
from handlers import start, settings, training

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def set_main_menu(bot: Bot):
    commands = [
        BotCommand(command="start", description="Bosh menyu / Mashqni boshlash"),
        BotCommand(command="stats", description="Mening natijalarim va statistika"),
        BotCommand(command="help", description="Qo'llanma va yordam"),
    ]
    await bot.set_my_commands(commands)

async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN aniqlanmadi! Iltimos, .env faylida BOT_TOKEN ni ko'rsating.")
        sys.exit(1)

    # Ma'lumotlar bazasini ishga tushirish
    init_db()
    logger.info("Ma'lumotlar bazasi tayyorlandi.")

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Routerlarni ulash
    dp.include_router(start.router)
    dp.include_router(settings.router)
    dp.include_router(training.router)

    await set_main_menu(bot)

    # Eski kutilayotgan yangilanishlarni tozalash
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot muvaffaqiyatli ishga tushdi va xabarlarni kutmoqda...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
