import os
import uuid
from typing import Annotated

import aiofiles
from fastapi import Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from image_processing_service.database import get_session
from image_processing_service.models import Image
from image_processing_service.services.exceptions import (
    ImageSaveError,
    InvalidImageError,
)
from image_processing_service.settings import settings


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


def get_image_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ImageService:
    return ImageService(session)
