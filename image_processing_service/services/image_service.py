import os
import uuid
from typing import Annotated

import aiofiles
from fastapi import Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from image_processing_service.database import get_session
from image_processing_service.models import Image
from image_processing_service.schemas.image_transform_schemas import (
    TransformationSchema,
)
from image_processing_service.services.exceptions import (
    ImageSaveError,
    InvalidImageError,
)
from image_processing_service.settings import settings
from image_processing_service.tasks import apply_transformations_async


class ImageService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_image(self, file: UploadFile, user_id: int) -> Image:
        if not file.content_type.startswith('image/'):
            raise InvalidImageError('Only images are allowed.')

        file_ext = os.path.splitext(file.filename)[1]
        filename = f'{uuid.uuid4()}{file_ext}'
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        try:
            async with aiofiles.open(file_path, 'wb') as buffer:
                while chunk := await file.read(1024 * 1024):  # 1MB por vez
                    await buffer.write(chunk)
        except Exception:
            raise ImageSaveError('Error while saving the image.')

        image = Image(
            filename=file.filename,
            url=file_path,
            user_id=user_id,
        )
        self.session.add(image)
        await self.session.commit()
        await self.session.refresh(image)

        return image

    async def get_image_by_id_and_user(
        self, image_id: int, user_id: int
    ) -> Image | None:
        result = await self.session.execute(
            select(Image).where(Image.id == image_id, Image.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_images_for_user(
        self, user_id: int, page: int, limit: int
    ) -> list[Image]:
        if page < 1 or limit < 1:
            raise ValueError('Page and limit must be greater than 0.')

        offset = (page - 1) * limit
        result = await self.session.execute(
            select(Image)
            .filter(Image.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def apply_transformations(
        self, image: Image, options: TransformationSchema
    ) -> Image:
        original_image_path = image.url
        format_ext = options.format or 'jpeg'
        new_filename = f'{uuid.uuid4()}.{format_ext.lower()}'
        new_image_path = os.path.join(settings.UPLOAD_DIR, new_filename)

        new_image = Image(
            filename=new_filename,
            url=new_image_path,
            user_id=image.user_id,
            original_image_id=image.id,
        )
        self.session.add(new_image)
        await self.session.commit()
        await self.session.refresh(new_image)

        apply_transformations_async.delay(
            original_image_path=original_image_path,
            new_image_path=new_image_path,
            transformations=options.model_dump(
                exclude_unset=True, mode='json'
            ),
        )

        return new_image


def get_image_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ImageService:
    return ImageService(session)
