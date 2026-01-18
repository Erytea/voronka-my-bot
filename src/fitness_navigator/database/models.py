"""
Модели данных для Фитнес-Навигатора
"""
from tortoise.models import Model
from tortoise import fields


class User(Model):
    """
    Модель пользователя Telegram
    """
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True, description="Уникальный ID пользователя Telegram")
    username = fields.CharField(max_length=255, null=True, description="Никнейм пользователя")
    first_name = fields.CharField(max_length=255, description="Имя пользователя")
    goal = fields.TextField(null=True, description="Главная цель пользователя из онбординга")
    limitations = fields.TextField(null=True, description="Ограничения (травмы, хронические состояния)")
    work_schedule = fields.CharField(max_length=500, null=True, description="Режим дня / рабочий график")
    onboarding_completed = fields.BooleanField(default=False, description="Завершён ли онбординг")
    created_at = fields.DatetimeField(auto_now_add=True, description="Дата регистрации")

    class Meta:
        table = "users"

    def __str__(self):
        return f"User({self.telegram_id}, {self.first_name})"


class DailyCheckin(Model):
    """
    Модель ежедневного чек-ина пользователя
    """
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        'models.User',
        related_name='checkins',
        on_delete=fields.CASCADE,
        description="Пользователь"
    )
    body_state = fields.IntField(description="Состояние тела (1-10)")
    available_time = fields.IntField(description="Доступное время в минутах")
    mood = fields.IntField(description="Настрой к активности (1-10)")
    suggested_action = fields.CharField(
        max_length=50,
        description="Предложенное действие: тренировка/восстановление/отдых"
    )
    action_details = fields.TextField(null=True, description="Детали действия (тип, продолжительность)")
    action_completed = fields.BooleanField(null=True, description="Выполнено ли действие (может быть Null)")
    checkin_date = fields.DateField(description="Дата чек-ина")
    created_at = fields.DatetimeField(auto_now_add=True, description="Дата и время создания записи")

    class Meta:
        table = "daily_checkins"

    def __str__(self):
        return f"Checkin({self.user_id}, {self.checkin_date}, {self.suggested_action})"
