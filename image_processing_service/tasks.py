from PIL import Image as PILImage
from PIL import ImageOps

from image_processing_service.celery import celery_app
from image_processing_service.services.exceptions import ImageSaveError


@celery_app.task
def apply_transformations_async(
    original_image_path: str, new_image_path: str, transformations: dict
):
    try:
        pil_image = PILImage.open(original_image_path)

        if transformations.get('resize'):
            pil_image = pil_image.resize((
                transformations['resize']['width'],
                transformations['resize']['height'],
            ))

        if transformations.get('crop'):
            box = (
                transformations['crop']['x'],
                transformations['crop']['y'],
                (
                    transformations['crop']['x']
                    + transformations['crop']['width']
                ),
                (
                    transformations['crop']['y']
                    + transformations['crop']['height']
                ),
            )
            pil_image = pil_image.crop(box)

        if transformations.get('rotate'):
            pil_image = pil_image.rotate(
                transformations['rotate'], expand=True
            )

        if transformations.get('filters'):
            if transformations['filters'].get('grayscale'):
                pil_image = ImageOps.grayscale(pil_image)
            if transformations['filters'].get('sepia'):
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

        format_ext: str = transformations.get('format', 'jpeg')
        pil_image.save(new_image_path, format=format_ext.upper())
    except Exception as e:
        raise ImageSaveError(f'Error applying transformations: {str(e)}')
