"""
Клавиатуры для чек-инов
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Импортируем общие клавиатуры
from src.fitness_navigator.keyboards.common import (
    get_numeric_keyboard,
    get_time_keyboard,
    get_action_confirmation_keyboard,
    get_completion_keyboard
)

# Экспортируем для удобства
__all__ = [
    'get_numeric_keyboard',
    'get_time_keyboard',
    'get_action_confirmation_keyboard',
    'get_completion_keyboard'
]
