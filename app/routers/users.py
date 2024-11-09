from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, insert, update

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth_service import get_current_user
from app.database.db_session import get_db
from app.models.user import User
from app.schemas import ViewsUser, UserResponse, CreateUser, UpdateUser

router = APIRouter(prefix='/user', tags=['User'])


@router.get('/all', response_model=list[ViewsUser])
async def all_users(
        db: Annotated[AsyncSession, Depends(get_db)],
        current_user: Annotated[dict, Depends(get_current_user)],
        skip: int = Query(0, ge=0),  # Параметр для пропуска пользователей
        limit: int = Query(10, gt=0)  # Параметр для ограничения количества пользователей
):
    """
    Получает список всех пользователей с учетом пагинации.

    Параметры:
    - db (AsyncSession): Асинхронная сессия базы данных.
    - current_user (dict): Данные текущего пользователя, полученные из зависимостей.
    - skip (int): Количество пользователей, которые нужно пропустить (по умолчанию 0).
    - limit (int): Максимальное количество пользователей для возврата (по умолчанию 10).

    Возвращает:
    - List[ViewsUser]: Список пользователей.

    Исключения:
    - HTTPException: Если текущий пользователь не является администратором (403).
    """
    if current_user.get('is_admin'):
        users_query = select(User).offset(skip).limit(limit)
        users = await db.execute(users_query)
        return users.scalars().all()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ запрещен. Необходимы права администратора.'
        )


@router.post('/create', response_model=UserResponse)
async def create_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        created_user: CreateUser,
        get_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Создает нового пользователя.

    Параметры:
    - db (AsyncSession): Асинхронная сессия базы данных.
    - created_user (CreateUser ): Данные для создания пользователя.
    - get_user (dict): Данные текущего пользователя, полученные из зависимостей.

    Возвращает:
    - dict: Словарь с статусом и сообщением о результате создания пользователя.

    Исключения:
    - HTTPException: Если текущий пользователь не является администратором (401).
    """
    if get_user.get('is_admin'):
        await db.execute(insert(User).values(
            name=created_user.name,
            email=created_user.email,
            password=created_user.password
        ))
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'message': "Пользователь успешно создан!",
            'transaction': {
                'status': 'Successful'
            }
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You must be an admin user for this'
        )


@router.put('/update_role/{user_id}')
async def update_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        user_id: int,
        updated_user: UpdateUser,
        current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Обновляет роль пользователя по его ID.

    Параметры:
    - db (AsyncSession): Асинхронная сессия базы данных.
    - user_id (int): ID пользователя, роль которого нужно обновить.
    - updated_user (UpdateUser ): Данные для обновления роли пользователя.
    - current_user (dict): Данные текущего пользователя, полученные из зависимостей.

    Возвращает:
    - dict: Словарь с сообщением об успешном обновлении пользователя.

    Исключения:
    - HTTPException: Если текущий пользователь не является администратором (403) или пользователь не найден (404).
    """
    if current_user.get('is_admin'):
        user = await db.scalar(select(User).where(User.id == user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Пользователь не найден'
            )
        await db.execute(update(User).where(User.id == user_id).values(
            role=updated_user.role,
            is_admin=updated_user.is_admin  # Обновление is_admin, если это необходимо
        ))
        await db.commit()
        return {
            'transaction': 'Пользователь успешно обновлен'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ запрещен. Необходимы права администратора.'
        )


@router.delete('/delete/{user_id}')
async def delete_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        user_id: int,
        current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Удаляет пользователя по его ID.

    Параметры:
    - db (AsyncSession): Асинхронная сессия базы данных.
    - user_id (int): ID пользователя, которого нужно удалить.
    - current_user (dict): Данные текущего пользователя, полученные из зависимостей.

    Возвращает:
    - dict: Словарь с сообщением об успешном удалении пользователя.

    Исключения:
    - HTTPException: Если текущий пользователь не является администратором (403) или пользователь не найден (404).
    """
    if current_user.get('is_admin'):
        user = await db.scalar(select(User).where(User.id == user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Пользователь не найден'
            )
        await db.delete(user)
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Пользователь успешно удален'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ запрещен. Необходимы права администратора.'
        )
