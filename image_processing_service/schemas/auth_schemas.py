from pydantic import BaseModel

from image_processing_service.settings import settings


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    expires_in: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
