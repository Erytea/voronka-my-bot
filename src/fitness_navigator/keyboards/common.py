"""
Общие клавиатуры для бота
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_numeric_keyboard(min_value: int = 1, max_value: int = 10, row_width: int = 5) -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с числовыми кнопками от min_value до max_value
    
    Args:
        min_value: Минимальное значение (по умолчанию 1)
        max_value: Максимальное значение (по умолчанию 10)
        row_width: Количество кнопок в ряду (по умолчанию 5)
    """
    buttons = [KeyboardButton(text=str(i)) for i in range(min_value, max_value + 1)]
    keyboard = ReplyKeyboardMarkup(
        keyboard=[buttons[i:i + row_width] for i in range(0, len(buttons), row_width)],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_yes_no_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с кнопками Да/Нет"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Создает главное меню бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Чек-ин дня")],
            [KeyboardButton(text="Статистика")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_time_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру для выбора времени (в минутах)"""
    time_options = [10, 15, 20, 30, 45, 60, 90, 120]
    buttons = [KeyboardButton(text=f"{t} мин") for t in time_options]
    keyboard = ReplyKeyboardMarkup(
        keyboard=[buttons[i:i + 4] for i in range(0, len(buttons), 4)],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_action_confirmation_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру для подтверждения/изменения действия"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Подтвердить")],
            [KeyboardButton(text="🔄 Изменить")],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_completion_keyboard() -> InlineKeyboardMarkup:
    """Создает inline клавиатуру для фиксации выполнения действия"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Выполнил", callback_data="action_completed_yes")],
            [InlineKeyboardButton(text="❌ Не выполнил", callback_data="action_completed_no")],
            [InlineKeyboardButton(text="⏭ Пропустить", callback_data="action_completed_skip")]
        ]
    )
    return keyboard
