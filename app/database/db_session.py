from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.database.db_connection import SessionLocal

import loguru


async def get_db() -> AsyncSession:
    """
    Асинхронный генератор для получения сессии базы данных.

    Используется для управления сессиями базы данных в приложении.
    Генерирует сессию, которая автоматически закрывается в конце блока.

    Возвращает:
        AsyncSession: Асинхронная сессия базы данных.

    Исключения:
        SQLAlchemyError: Возникает при ошибках SQLAlchemy.
    """
    async with SessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            loguru.logger.error(f"Произошла ошибка: {e}")
            await session.rollback()  # Откатываем сессию вместо фиксации
            raise
