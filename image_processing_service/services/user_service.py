from models import User
from schemas.user_schemas import UserCreateSchema
from security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: UserCreateSchema):
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


def get_user_service(session: AsyncSession):
    return UserService(session)
