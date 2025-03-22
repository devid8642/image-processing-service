from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from image_processing_service.schemas.auth_schemas import TokenSchema
from image_processing_service.schemas.user_schemas import UserCreateSchema
from image_processing_service.security import (
    create_access_token,
)
from image_processing_service.services.user_service import (
    UserService,
    get_user_service,
)
from image_processing_service.utils.hashing import verify_password

auth_router = APIRouter()


@auth_router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=TokenSchema,
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


@auth_router.post(
    '/login',
    status_code=status.HTTP_200_OK,
    response_model=TokenSchema,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Incorrect username or password',
            'content': {
                'application/json': {
                    'example': {'detail': 'Incorrect username or password'}
                }
            },
        },
    },
)
async def login(
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    user = await user_service.get_user(login_data.username)

    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
        )

    access_token = create_access_token(data={'sub': user.username})

    return {'access_token': access_token, 'token_type': 'bearer'}
