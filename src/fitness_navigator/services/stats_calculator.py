"""
Расчет статистики для пользователя
"""
from datetime import date, timedelta
from typing import Dict, List, Optional
from src.fitness_navigator.database.models import User, DailyCheckin


async def get_checkins_for_period(
    user: User,
    days: int = 7
) -> List[DailyCheckin]:
    """
    Получает чек-ины пользователя за указанный период
    
    Args:
        user: Пользователь
        days: Количество дней для выборки (по умолчанию 7)
    
    Returns:
        Список чек-инов
    """
    start_date = date.today() - timedelta(days=days)
    checkins = await DailyCheckin.filter(
        user=user,
        checkin_date__gte=start_date
    ).order_by("checkin_date")
    
    return checkins


async def calculate_statistics(user: User, days: int = 7) -> Dict:
    """
    Рассчитывает статистику за период
    
    Args:
        user: Пользователь
        days: Количество дней для анализа (7 или 30)
    
    Returns:
        Словарь со статистикой:
        - regularity: количество дней с активностью
        - total_checkins: всего чек-инов
        - action_distribution: распределение по типам действий
        - avg_body_state: среднее состояние тела
        - avg_mood: средний настрой
        - completed_count: количество выполненных действий
        - completion_rate: процент выполнения
    """
    checkins = await get_checkins_for_period(user, days)
    
    if not checkins:
        return {
            "regularity": 0,
            "total_checkins": 0,
            "action_distribution": {},
            "avg_body_state": 0,
            "avg_mood": 0,
            "completed_count": 0,
            "completion_rate": 0
        }
    
    # Регулярность (уникальные даты с чек-инами)
    unique_dates = len(set(c.checkin_date for c in checkins))
    
    # Распределение по типам действий
    action_distribution = {}
    for checkin in checkins:
        action = checkin.suggested_action
        action_distribution[action] = action_distribution.get(action, 0) + 1
    
    # Средние значения
    avg_body_state = sum(c.body_state for c in checkins) / len(checkins)
    avg_mood = sum(c.mood for c in checkins) / len(checkins)
    
    # Выполнение действий
    completed_checkins = [c for c in checkins if c.action_completed is True]
    completed_count = len(completed_checkins)
    completion_rate = (completed_count / len(checkins) * 100) if checkins else 0
    
    return {
        "regularity": unique_dates,
        "total_checkins": len(checkins),
        "action_distribution": action_distribution,
        "avg_body_state": round(avg_body_state, 1),
        "avg_mood": round(avg_mood, 1),
        "completed_count": completed_count,
        "completion_rate": round(completion_rate, 1)
    }
