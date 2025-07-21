import asyncio
import telegram
from telegram.ext import Application
import logging
import pytz
import datetime
import os

# Налаштування логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Налаштування бота
TOKEN = os.getenv('TOKEN')  # Отримуємо з змінних середовища
GROUP_ID = int(os.getenv('GROUP_ID'))  # Отримуємо з змінних середовища
bot = telegram.Bot(token=TOKEN)

# Час для відправки опитування
TARGET_HOUR = 16
TARGET_MINUTE = 09

async def send_poll_async():
    try:
        await bot.send_poll(
            chat_id=GROUP_ID,
            question="Хто завтра на роботу?",
            options=["✅ Так", "❌ Ні"],
            is_anonymous=False,
            allows_multiple_answers=False
        )
        logger.info("Опитування надіслано!")
        return True
    except Exception as e:
        logger.error(f"Помилка при відправці опитування: {e}", exc_info=True)
        return False

async def main():
    try:
        # Ініціалізація бота
        application = Application.builder().token(TOKEN).build()
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        logger.info("Бот запущено успішно")

        while True:
            # Отримуємо поточний час у київському часовому поясі
            now = datetime.datetime.now(pytz.timezone('Europe/Kyiv'))
            logger.info(f"Поточний київський час: {now} (пояс: {now.tzinfo})")

            # Визначаємо цільовий час сьогодні
            target_time_today = now.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)
            
            # Якщо час минув, плануємо на завтра
            if now > target_time_today:
                target_time_tomorrow = target_time_today + datetime.timedelta(days=1)
                seconds_until_target = (target_time_tomorrow - now).total_seconds()
            else:
                seconds_until_target = (target_time_today - now).total_seconds()

            logger.info(f"Чекаємо {seconds_until_target} секунд до {TARGET_HOUR}:{TARGET_MINUTE}")
            await asyncio.sleep(seconds_until_target)
            sent = await send_poll_async()
            if sent:
                logger.info("Опитування відправлено в заданий час")
            
            # Чекаємо 1 хвилину перед наступною перевіркою
            await asyncio.sleep(60)
            
    except Exception as e:
        logger.error(f"Критична помилка в main: {e}", exc_info=True)
        # Чекаємо перед перезапуском, щоб уникнути швидкого зациклення
        await asyncio.sleep(60)
        # Перезапускаємо main
        await main()

if __name__ == '__main__':
    asyncio.run(main())
