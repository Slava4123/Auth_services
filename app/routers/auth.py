from datetime import timedelta

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.database.db_session import get_db
from app.models.user import User
from app.schemas import CreateUser
from app.auth_service import authenticate_normal_user, create_access_token, bcrypt_context

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/')
async def create_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        created_user: CreateUser
):
    """
    Создает нового пользователя.
    Параметры:
    - db (AsyncSession): Асинхронная сессия базы данных.
    - created_user (CreateUser): Данные для создания пользователя, включая имя, email и пароль.
    Возвращает:
    - dict: Словарь со статусом и сообщением о результате создания пользователя.
    """
    try:
        await db.execute(insert(User).values(
            name=created_user.name,
            email=created_user.email,
            password=bcrypt_context.hash(created_user.password),
            role='client',
            is_admin=False
        ))
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Пользователь успешно создан'
        }
    except IntegrityError:
        await db.rollback()
        return {'transaction': 'Пользователь с таким именем или email уже существует'}
    except Exception as e:
        return {'transaction': f'Ошибка: {str(e)}'}


@router.post('/token')
async def login(
        db: Annotated[AsyncSession, Depends(get_db)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    Аутентифицирует пользователя и выдает токен доступа.
    Параметры:
    - db (AsyncSession): Асинхронная сессия базы данных.
    - form_data (OAuth2PasswordRequestForm): Данные для аутентификации, включая имя пользователя и пароль.
    Возвращает:
    - dict: Словарь с токеном доступа и типом токена.
    """
    user = await authenticate_normal_user(db, form_data.username, form_data.password)
    token = await create_access_token(user.name, user.id, user.role, user.is_admin,
                                      expires_delta=timedelta(minutes=20))
    return {
        'access_token': token,
        'token_type': 'bearer'
    }
