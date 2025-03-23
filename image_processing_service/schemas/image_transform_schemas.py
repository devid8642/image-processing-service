from typing import Optional

from pydantic import BaseModel


class ResizeOptions(BaseModel):
    width: int
    height: int


class CropOptions(BaseModel):
    width: int
    height: int
    x: int
    y: int


class FilterOptions(BaseModel):
    grayscale: Optional[bool] = False
    sepia: Optional[bool] = False


class TransformationSchema(BaseModel):
    resize: Optional[ResizeOptions] = None
    crop: Optional[CropOptions] = None
    rotate: Optional[int] = None  # graus
    format: Optional[str] = None  # ex: 'jpeg', 'png'
    filters: Optional[FilterOptions] = None
