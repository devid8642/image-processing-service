from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from image_processing_service.models import User
from image_processing_service.schemas.image_schemas import ImageSchema
from image_processing_service.schemas.image_transform_schemas import (
    TransformationSchema,
)
from image_processing_service.security import get_current_user
from image_processing_service.services.exceptions import (
    ImageSaveError,
    InvalidImageError,
)
from image_processing_service.services.image_service import (
    ImageService,
    get_image_service,
)

image_router = APIRouter()


@image_router.post(
    '/images',
    status_code=status.HTTP_201_CREATED,
    response_model=ImageSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'description': 'Invalid image',
            'content': {
                'application/json': {
                    'example': {'detail': 'Only images are allowed'}
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'description': 'Error while saving the image',
            'content': {
                'application/json': {
                    'example': {'detail': 'Error while saving the image'}
                }
            },
        },
    },
)
async def upload_image(
    user: Annotated[User, Depends(get_current_user)],
    image_service: Annotated[ImageService, Depends(get_image_service)],
    file: UploadFile,
):
    try:
        image = await image_service.save_image(file=file, user_id=user.id)
    except InvalidImageError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except ImageSaveError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return image


@image_router.post(
    '/images/{id}/transform',
    response_model=ImageSchema,
    responses={
        status.HTTP_404_NOT_FOUND: {
            'description': 'Image not found',
            'content': {
                'application/json': {'example': {'detail': 'Image not found'}}
            },
        },
    },
)
async def transform_image(
    id: int,
    user: Annotated[User, Depends(get_current_user)],
    image_service: Annotated[ImageService, Depends(get_image_service)],
    transformations: TransformationSchema,
):
    image = await image_service.get_image_by_id_and_user(
        image_id=id, user_id=user.id
    )
    if not image:
        raise HTTPException(status_code=404, detail='Image not found')

    transformed_image = await image_service.apply_transformations(
        image, transformations
    )
    return transformed_image
