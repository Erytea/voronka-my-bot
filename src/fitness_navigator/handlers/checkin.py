"""
Обработчики для ежедневного чек-ина
"""
from datetime import date
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from src.fitness_navigator.database.models import User, DailyCheckin
from src.fitness_navigator.services.decision_engine import suggest_action
from src.fitness_navigator.keyboards.common import (
    get_numeric_keyboard,
    get_time_keyboard,
    get_action_confirmation_keyboard,
    get_main_menu_keyboard
)
from src.fitness_navigator.keyboards.checkin import get_completion_keyboard

router = Router(name="checkin")


class CheckinStates(StatesGroup):
    """Состояния FSM для чек-ина"""
    waiting_body_state = State()
    waiting_available_time = State()
    waiting_mood = State()
    confirming_action = State()


@router.message(Command("checkin"))
@router.message(F.text == "Чек-ин дня")
async def cmd_checkin(message: Message, state: FSMContext):
    """Начало процесса чек-ина"""
    # Проверка, прошел ли пользователь онбординг
    user = await User.get_or_none(telegram_id=message.from_user.id)
    
    if not user or not user.onboarding_completed:
        await message.answer(
            "Сначала нужно пройти онбординг. Используй команду /start."
        )
        return
    
    # Сброс состояния
    await state.clear()
    
    await message.answer(
        "Давай проверим, как ты себя чувствуешь сегодня.\n\n"
        "Как ты оцениваешь своё <b>состояние тела</b> от 1 до 10?\n"
        "(1 = совсем нет сил, 10 = полон энергии)",
        reply_markup=get_numeric_keyboard(1, 10)
    )
    await state.set_state(CheckinStates.waiting_body_state)


@router.message(CheckinStates.waiting_body_state)
async def process_body_state(message: Message, state: FSMContext):
    """Обработка состояния тела"""
    try:
        body_state = int(message.text)
        if not (1 <= body_state <= 10):
            raise ValueError
        
        await state.update_data(body_state=body_state)
        
        await message.answer(
            f"Хорошо, состояние тела: {body_state}/10.\n\n"
            "Сколько <b>минут</b> сегодня можешь уделить телу?",
            reply_markup=get_time_keyboard()
        )
        await state.set_state(CheckinStates.waiting_available_time)
    except (ValueError, TypeError):
        await message.answer(
            "Пожалуйста, выбери число от 1 до 10.",
            reply_markup=get_numeric_keyboard(1, 10)
        )


@router.message(CheckinStates.waiting_available_time)
async def process_available_time(message: Message, state: FSMContext):
    """Обработка доступного времени"""
    text = message.text.strip().lower()
    
    # Парсинг времени из текста (например, "30 мин", "30", "30 минут")
    try:
        if "мин" in text:
            time_str = text.replace("мин", "").replace("минут", "").strip()
            available_time = int(time_str)
        else:
            available_time = int(text)
    except ValueError:
        await message.answer(
            "Пожалуйста, укажи время в минутах. Например: 30 или 30 мин",
            reply_markup=get_time_keyboard()
        )
        return
    
    if available_time < 5:
        available_time = 5
    elif available_time > 240:
        available_time = 240
    
    await state.update_data(available_time=available_time)
    
    await message.answer(
        f"Понял, {available_time} минут.\n\n"
        "Теперь оцени свой <b>настрой к активности</b> от 1 до 10.\n"
        "(1 = не готов вообще, 10 = готов к интенсиву)",
        reply_markup=get_numeric_keyboard(1, 10)
    )
    await state.set_state(CheckinStates.waiting_mood)


@router.message(CheckinStates.waiting_mood)
async def process_mood(message: Message, state: FSMContext):
    """Обработка настроя и генерация предложения"""
    try:
        mood = int(message.text)
        if not (1 <= mood <= 10):
            raise ValueError
        
        data = await state.get_data()
        body_state = data.get("body_state")
        available_time = data.get("available_time")
        
        # Получение пользователя
        user = await User.get(telegram_id=message.from_user.id)
        
        # Генерация предложения через decision engine
        suggestion = suggest_action(body_state, available_time, mood, user)
        
        # Сохранение предложения в состоянии для подтверждения
        await state.update_data(
            mood=mood,
            suggested_action=suggestion["action"],
            action_details=suggestion["details"],
            reason=suggestion["reason"]
        )
        
        # Формирование сообщения с предложением
        suggestion_text = (
            f"<b>Моё предложение на сегодня:</b>\n\n"
            f"<b>{suggestion['action'].upper()}</b>\n"
            f"{suggestion['details']}\n\n"
            f"<i>{suggestion['reason']}</i>\n\n"
            "Подтверди это действие или выбери другое."
        )
        
        await message.answer(
            suggestion_text,
            reply_markup=get_action_confirmation_keyboard()
        )
        await state.set_state(CheckinStates.confirming_action)
        
    except (ValueError, TypeError):
        await message.answer(
            "Пожалуйста, выбери число от 1 до 10.",
            reply_markup=get_numeric_keyboard(1, 10)
        )


@router.message(CheckinStates.confirming_action, F.text == "✅ Подтвердить")
async def confirm_action(message: Message, state: FSMContext):
    """Подтверждение действия и сохранение чек-ина"""
    data = await state.get_data()
    
    user = await User.get(telegram_id=message.from_user.id)
    
    # Создание записи чек-ина
    checkin = await DailyCheckin.create(
        user=user,
        body_state=data.get("body_state"),
        available_time=data.get("available_time"),
        mood=data.get("mood"),
        suggested_action=data.get("suggested_action"),
        action_details=data.get("action_details"),
        checkin_date=date.today()
    )
    
    await state.clear()
    
    confirmation_text = (
        "Отлично! Я зафиксировал твоё решение на сегодня.\n\n"
        "В конце дня можешь сообщить, выполнил ли ты действие. "
        "Это поможет мне лучше понимать твои паттерны."
    )
    
    await message.answer(
        confirmation_text,
        reply_markup=get_main_menu_keyboard()
    )
    
    # Предложение зафиксировать выполнение через некоторое время (можно реализовать через scheduler)
    # Сейчас просто показываем inline кнопку
    await message.answer(
        "Выполнил действие?",
        reply_markup=get_completion_keyboard()
    )


@router.message(CheckinStates.confirming_action, F.text == "❌ Отмена")
async def cancel_action(message: Message, state: FSMContext):
    """Отмена чек-ина"""
    await state.clear()
    await message.answer(
        "Чек-ин отменен. Если передумаешь, используй команду /checkin или кнопку «Чек-ин дня».",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(CheckinStates.confirming_action, F.text == "🔄 Изменить")
async def change_action(message: Message, state: FSMContext):
    """Начать чек-ин заново"""
    await state.clear()
    await cmd_checkin(message, state)


@router.callback_query(F.data.startswith("action_completed_"))
async def process_completion(callback: CallbackQuery, state: FSMContext):
    """Обработка фиксации выполнения действия"""
    action_type = callback.data.split("_")[-1]
    
    # Получаем последний чек-ин пользователя за сегодня
    user = await User.get(telegram_id=callback.from_user.id)
    today_checkin = await DailyCheckin.filter(
        user=user,
        checkin_date=date.today()
    ).order_by("-created_at").first()
    
    if today_checkin:
        if action_type == "yes":
            today_checkin.action_completed = True
            response_text = "Отлично! Зафиксировал выполнение."
        elif action_type == "no":
            today_checkin.action_completed = False
            response_text = "Понял. Ничего страшного, завтра будет новый день."
        else:  # skip
            response_text = "Хорошо, пропускаю."
        
        if action_type != "skip":
            await today_checkin.save()
        
        await callback.message.edit_text(response_text)
    else:
        await callback.answer("Не найден чек-ин за сегодня.", show_alert=True)
    
    await callback.answer()
