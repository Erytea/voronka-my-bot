from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "telegram_id" BIGINT NOT NULL UNIQUE /* Уникальный ID пользователя Telegram */,
    "username" VARCHAR(255) /* Никнейм пользователя */,
    "first_name" VARCHAR(255) NOT NULL /* Имя пользователя */,
    "goal" TEXT /* Главная цель пользователя из онбординга */,
    "limitations" TEXT /* Ограничения (травмы, хронические состояния) */,
    "work_schedule" VARCHAR(500) /* Режим дня \/ рабочий график */,
    "onboarding_completed" INT NOT NULL DEFAULT 0 /* Завершён ли онбординг */,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP /* Дата регистрации */
) /* Модель пользователя Telegram */;
CREATE TABLE IF NOT EXISTS "daily_checkins" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "body_state" INT NOT NULL /* Состояние тела (1-10) */,
    "available_time" INT NOT NULL /* Доступное время в минутах */,
    "mood" INT NOT NULL /* Настрой к активности (1-10) */,
    "suggested_action" VARCHAR(50) NOT NULL /* Предложенное действие: тренировка\/восстановление\/отдых */,
    "action_details" TEXT /* Детали действия (тип, продолжительность) */,
    "action_completed" INT /* Выполнено ли действие (может быть Null) */,
    "checkin_date" DATE NOT NULL /* Дата чек-ина */,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP /* Дата и время создания записи */,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE /* Пользователь */
) /* Модель ежедневного чек-ина пользователя */;
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "Q75MXf0HMSkuqg=="
)
