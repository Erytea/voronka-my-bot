"""
Инициализация базы данных Tortoise ORM
"""
from tortoise import Tortoise
from src.fitness_navigator.config import settings

# AICODE-NOTE: Используем SQLite для простоты MVP, не требует отдельного сервера БД

TORTOISE_ORM = {
    "connections": {
        "default": settings.database_url
    },
    "apps": {
        "models": {
            "models": ["src.fitness_navigator.database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init_db():
    """Инициализация подключения к базе данных"""
    await Tortoise.init(config=TORTOISE_ORM)
    # Генерируем схемы БД
    await Tortoise.generate_schemas()


async def close_db():
    """Закрытие подключения к базе данных"""
    await Tortoise.close_connections()
