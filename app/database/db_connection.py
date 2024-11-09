from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import loguru

from dotenv import load_dotenv

load_dotenv()
DB_NAME = config('DB_NAME')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST')
DB_PORT = config('DB_PORT')

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
async def check_connection():
    """
    Проверяет подключение к базе данных.
    Устанавливает соединение с базой данных и выполняет
    запрос для проверки работоспособности. Выводит сообщение
    о статусе подключения.
    Исключения:
        Exception: Возникает при ошибках подключения к базе данных.
    """
    try:
        async with engine.connect():
            loguru.logger.info("Подключение к базе данных успешно установлено.")
    except Exception as e:
        loguru.logger.error(f"Ошибка подключения к базе данных: {e}")
class Base(DeclarativeBase):
    """
    Базовый класс для моделей SQLAlchemy.
    Используется в качестве основы для всех моделей в приложении.
    Позволяет использовать декларативный стиль определения моделей.
    """
    pass