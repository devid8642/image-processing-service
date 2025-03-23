from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ImageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    url: str
    uploaded_at: datetime
    user_id: int
    original_image_id: int | None = None
