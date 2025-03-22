from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from image_processing_service.database import get_session
from image_processing_service.models import User
from image_processing_service.schemas.user_schemas import UserCreateSchema
from image_processing_service.utils.hashing import get_password_hash


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: UserCreateSchema) -> User:
        existing_user = await self.session.scalar(
            select(User).where(User.username == user.username)
        )
        if existing_user:
            raise ValueError('User already exists')

        new_user = User(
            username=user.username, password=get_password_hash(user.password)
        )

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return new_user

    async def get_user(self, username: str) -> User:
        user = await self.session.scalar(
            select(User).where(User.username == username)
        )
        return user


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    return UserService(session)
