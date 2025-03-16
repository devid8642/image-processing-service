from typing import Annotated

from database import get_session
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.auth_schemas import TokenSchema
from schemas.user_schemas import UserCreateSchema
from security import create_access_token
from services.user_service import get_user_service
from sqlalchemy.ext.asyncio import AsyncSession

auth_router = APIRouter()
Session = Annotated[AsyncSession, Depends(get_session)]


@auth_router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {
            'description': 'Username already exists',
            'content': {
                'application/json': {
                    'example': {'detail': 'Username already exists'}
                }
            },
        },
    },
    response_model=TokenSchema,
)
async def register(user: UserCreateSchema, session: Session):
    user_service = get_user_service(session)

    try:
        user = await user_service.create_user(user)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Username already exists',
        )

    access_token = create_access_token(data={'sub': user.username})

    return {'access_token': access_token, 'token_type': 'bearer'}
