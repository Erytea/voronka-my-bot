"""
Обработчики базовых команд: /start и онбординг
"""
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from src.fitness_navigator.database.models import User
from src.fitness_navigator.keyboards.common import (
    get_yes_no_keyboard,
    get_main_menu_keyboard
)

router = Router(name="common")


class OnboardingStates(StatesGroup):
    """Состояния FSM для онбординга"""
    waiting_goal = State()
    waiting_limitations = State()
    waiting_work_schedule = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    # Сброс состояния FSM
    await state.clear()
    
    # Получение или создание пользователя
    user, created = await User.get_or_create(
        telegram_id=message.from_user.id,
        defaults={
            "first_name": message.from_user.first_name or "Пользователь",
            "username": message.from_user.username,
        }
    )
    
    # Приветствие
    welcome_text = (
        "Привет! Я твой Фитнес-Навигатор. "
        "Моя задача — каждый день помогать тебе принимать одно адекватное решение для тела. "
        "Не мотивировать, не давить — просто предложить, что подходит прямо сейчас.\n\n"
    )
    
    if user.onboarding_completed:
        welcome_text += (
            "Рад снова тебя видеть! Используй кнопки ниже для взаимодействия.\n\n"
            "💡 <b>Доступные команды:</b>\n"
            "• /checkin — ежедневный чек-ин\n"
            "• /stats — статистика"
        )
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu_keyboard()
        )
    else:
        welcome_text += (
            "Давай начнём с твоих целей и ограничений. "
            "Это поможет мне предлагать тебе подходящие решения.\n\n"
            "Какая у тебя главная цель? "
            "(Например: здоровье, энергия, форма, конкретная задача)"
        )
        await message.answer(welcome_text)
        await state.set_state(OnboardingStates.waiting_goal)


@router.message(OnboardingStates.waiting_goal)
async def process_goal(message: Message, state: FSMContext):
    """Обработка цели пользователя"""
    goal = message.text.strip()
    await state.update_data(goal=goal)
    
    await message.answer(
        "Понял. А какие у тебя ограничения? "
        "(Например: травмы, хронические состояния, проблемы со здоровьем). "
        "Если ограничений нет, напиши «нет».",
        reply_markup=get_yes_no_keyboard()
    )
    await state.set_state(OnboardingStates.waiting_limitations)


@router.message(OnboardingStates.waiting_limitations)
async def process_limitations(message: Message, state: FSMContext):
    """Обработка ограничений пользователя"""
    limitations = message.text.strip()
    # Если пользователь выбрал "Нет", сохраняем пустую строку
    if limitations.lower() in ["нет", "no", "нет ограничений"]:
        limitations = ""
    
    await state.update_data(limitations=limitations)
    
    await message.answer(
        "Хорошо, учту. Последний вопрос: какой у тебя режим дня? "
        "(Например: рабочий график, когда обычно есть время для активности, особенности распорядка). "
        "Можешь описать кратко.",
        reply_markup=None
    )
    await state.set_state(OnboardingStates.waiting_work_schedule)


@router.message(OnboardingStates.waiting_work_schedule)
async def process_work_schedule(message: Message, state: FSMContext):
    """Обработка режима дня и завершение онбординга"""
    work_schedule = message.text.strip()
    data = await state.get_data()
    
    # Обновление данных пользователя
    user = await User.get(telegram_id=message.from_user.id)
    user.goal = data.get("goal")
    user.limitations = data.get("limitations", "")
    user.work_schedule = work_schedule
    user.onboarding_completed = True
    await user.save()
    
    # Очистка состояния FSM
    await state.clear()
    
    completion_text = (
        "Отлично! Теперь я знаю твои цели, ограничения и режим дня. "
        "Готов помогать тебе принимать решения каждый день.\n\n"
        "Используй кнопку <b>«Чек-ин дня»</b> каждый день, чтобы получить персональное предложение "
        "для твоего тела. Или воспользуйся командой /checkin.\n\n"
        "Помни: отдых и восстановление — это тоже важная часть заботы о себе. "
        "Я не буду давить или мотивировать. Просто помогу выбрать то, что подходит именно сейчас."
    )
    
    await message.answer(
        completion_text,
        reply_markup=get_main_menu_keyboard()
    )
