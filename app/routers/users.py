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
    if current_user.get('is_admin'):
        # Выполняем запрос с учетом пагинации
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
async def update_user(db: Annotated[AsyncSession, Depends(get_db)], user_id: int,
                      updated_user: UpdateUser, current_user: Annotated[dict, Depends(get_current_user)]):
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
async def delete_user(db: Annotated[AsyncSession, Depends(get_db)], user_id: int,
                      current_user: Annotated[dict, Depends(get_current_user)]):
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
