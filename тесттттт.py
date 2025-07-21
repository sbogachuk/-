import asyncio
import telegram
from telegram.ext import Application
import logging
import pytz
import datetime

# Налаштування логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Налаштування бота
TOKEN = '7642593461:AAHb_XPxyReVjL42PRTZoyoUioQzuv_Ym3c'
GROUP_ID = -4923200694
bot = telegram.Bot(token=TOKEN)

# Час для відправки опитування
TARGET_HOUR = 14
TARGET_MINUTE = 35

async def send_poll_async():
    try:
        await bot.send_poll(
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

async def main():
    application = Application.builder().token(TOKEN).build()
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Отримуємо поточний час у київському часовому поясі
    now = datetime.datetime.now(pytz.timezone('Europe/Kyiv'))
    logging.info(f"Поточний київський час: {now} (пояс: {now.tzinfo})")

    # Перевіряємо, чи поточний час після 14:29
    target_time_today = now.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)
    if now >= target_time_today:
        # Якщо час уже минув, відправляємо опитування одразу
        sent = await send_poll_async()
        if sent:
            logging.info("Опитування відправлено одразу, оскільки час уже минув")
    else:
        # Розраховуємо, скільки секунд залишилося до 14:29
        seconds_until_target = (target_time_today - now).total_seconds()
        logging.info(f"Чекаємо {seconds_until_target} секунд до {TARGET_HOUR}:{TARGET_MINUTE}")
        await asyncio.sleep(seconds_until_target)
        sent = await send_poll_async()
        if sent:
            logging.info("Опитування відправлено в заданий час")

    # Залишаємо бота активним
    while True:
        await asyncio.sleep(60)

if __name__ == '__main__':
    asyncio.run(main())