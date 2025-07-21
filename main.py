import asyncio
import logging
from telegram.ext import Application
import pytz
import datetime
import os

TOKEN = os.getenv("TELEGRAM_TOKEN", "7642593461:AAHb_XPxyReVjL42PRTZoyoUioQzuv_Ym3c")
GROUP_ID = int(os.getenv("GROUP_ID", "-4923200694"))

TARGET_HOUR = 16
TARGET_MINUTE = 38

logging.basicConfig(level=logging.INFO)

async def send_poll_async(application):
    try:
        await application.bot.send_poll(
            chat_id=GROUP_ID,
            question="Хто завтра на роботу?",
            options=["✅ Так", "❌ Ні"],
            is_anonymous=False,
            allows_multiple_answers=False
        )
        logging.info("Опитування надіслано!")
        return True
    except Exception as e:
        logging.error(f"Помилка при відправці опитування: {e}")
        return False

async def scheduler(application):
    while True:
        now = datetime.datetime.now(pytz.timezone('Europe/Kyiv'))
        target_time = now.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)
        if now > target_time:
            target_time += datetime.timedelta(days=1)
        delay = (target_time - now).total_seconds()
        logging.info(f"Чекаємо {delay} секунд до {target_time}")
        await asyncio.sleep(delay)
        await send_poll_async(application)

async def main():
    application = Application.builder().token(TOKEN).build()
    # scheduler запускається в окремому таску
    asyncio.create_task(scheduler(application))
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
