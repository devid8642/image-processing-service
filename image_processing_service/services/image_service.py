import os
import uuid
from typing import Annotated

import aiofiles
from fastapi import Depends, UploadFile
from PIL import Image as PILImage
from PIL import ImageOps
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
        original_path = image.url
        try:
            pil_image = PILImage.open(original_path)

            if options.resize:
                pil_image = pil_image.resize((
                    options.resize.width,
                    options.resize.height,
                ))

            if options.crop:
                box = (
                    options.crop.x,
                    options.crop.y,
                    options.crop.x + options.crop.width,
                    options.crop.y + options.crop.height,
                )
                pil_image = pil_image.crop(box)

            if options.rotate:
                pil_image = pil_image.rotate(options.rotate, expand=True)

            if options.filters:
                if options.filters.grayscale:
                    pil_image = ImageOps.grayscale(pil_image)
                if options.filters.sepia:
                    sepia = PILImage.new('RGB', pil_image.size)
                    pixels = pil_image.convert('RGB').load()
                    for y in range(pil_image.size[1]):
                        for x in range(pil_image.size[0]):
                            r, g, b = pixels[x, y]
                            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                            sepia.putpixel(
                                (x, y),
                                (min(tr, 255), min(tg, 255), min(tb, 255)),
                            )
                    pil_image = sepia

            # Convert format
            format_ext = options.format or 'jpeg'
            new_filename = f'{uuid.uuid4()}.{format_ext.lower()}'
            new_path = os.path.join(settings.UPLOAD_DIR, new_filename)
            pil_image.save(new_path, format=format_ext.upper())

            new_image = Image(
                filename=new_filename,
                url=new_path,
                user_id=image.user_id,
                original_image_id=image.id,
            )
            self.session.add(new_image)
            await self.session.commit()
            await self.session.refresh(new_image)

            return new_image

        except Exception as e:
            raise ImageSaveError(f'Error applying transformations: {str(e)}')


def get_image_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ImageService:
    return ImageService(session)
