"""
Точка входа для Telegram-бота "Фитнес-Навигатор"
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.fitness_navigator.config import settings
from src.fitness_navigator.database.core import init_db, close_db
from src.fitness_navigator.handlers import common, checkin, stats

# AICODE-NOTE: Используем polling вместо webhook для простоты MVP
# AICODE-TODO: Добавить middleware для логирования ошибок

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    # Проверка токена
    if not settings.bot_token:
        logger.error("BOT_TOKEN не установлен! Проверьте файл .env")
        return
    
    # Инициализация бота и диспетчера
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Подключение роутеров
    dp.include_router(common.router)
    dp.include_router(checkin.router)
    dp.include_router(stats.router)
    
    # Подключение жизненного цикла БД
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    logger.info("Бот запускается...")
    
    # Запуск polling
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def on_startup():
    """Выполняется при запуске бота"""
    logger.info("Инициализация базы данных...")
    await init_db()
    logger.info("База данных инициализирована")


async def on_shutdown():
    """Выполняется при остановке бота"""
    logger.info("Закрытие подключений...")
    await close_db()
    logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
