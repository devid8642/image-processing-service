from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from image_processing_service.schemas.auth_schemas import TokenSchema
from image_processing_service.schemas.user_schemas import UserCreateSchema
from image_processing_service.security import create_access_token
from image_processing_service.services.user_service import (
    UserService,
    get_user_service,
)

auth_router = APIRouter()


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
async def register(
    user: UserCreateSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        user = await user_service.create_user(user)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Username already exists',
        )

    access_token = create_access_token(data={'sub': user.username})

    return {'access_token': access_token, 'token_type': 'bearer'}
