"""
Обработчики для статистики
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.fitness_navigator.database.models import User
from src.fitness_navigator.services.stats_calculator import (
    calculate_statistics,
    get_checkins_for_period
)
from src.fitness_navigator.services.insights import (
    generate_insights,
    format_statistics_message
)
from src.fitness_navigator.keyboards.common import get_main_menu_keyboard

router = Router(name="stats")


@router.message(Command("stats"))
@router.message(F.text == "Статистика")
async def cmd_stats(message: Message, state: FSMContext):
    """Показ статистики за 7 дней по умолчанию"""
    await state.clear()
    
    # Проверка, прошел ли пользователь онбординг
    user = await User.get_or_none(telegram_id=message.from_user.id)
    
    if not user or not user.onboarding_completed:
        await message.answer(
            "Сначала нужно пройти онбординг. Используй команду /start."
        )
        return
    
    # Статистика за 7 дней
    stats = await calculate_statistics(user, days=7)
    stats["days"] = 7
    
    checkins = await get_checkins_for_period(user, days=7)
    insights = generate_insights(checkins, stats)
    
    stats_message = format_statistics_message(stats, insights)
    
    await message.answer(
        stats_message,
        reply_markup=get_main_menu_keyboard()
    )
    
    # Предложение посмотреть статистику за 30 дней
    await message.answer(
        "Хочешь посмотреть статистику за последние 30 дней? Напиши /stats30"
    )


@router.message(Command("stats30"))
async def cmd_stats30(message: Message, state: FSMContext):
    """Показ статистики за 30 дней"""
    await state.clear()
    
    user = await User.get_or_none(telegram_id=message.from_user.id)
    
    if not user or not user.onboarding_completed:
        await message.answer(
            "Сначала нужно пройти онбординг. Используй команду /start."
        )
        return
    
    # Статистика за 30 дней
    stats = await calculate_statistics(user, days=30)
    stats["days"] = 30
    
    checkins = await get_checkins_for_period(user, days=30)
    insights = generate_insights(checkins, stats)
    
    stats_message = format_statistics_message(stats, insights)
    
    await message.answer(
        stats_message,
        reply_markup=get_main_menu_keyboard()
    )
