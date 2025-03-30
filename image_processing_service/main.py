import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from image_processing_service.routers.auth_router import auth_router
from image_processing_service.routers.image_router import image_router
from image_processing_service.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield


app = FastAPI(
    title='Image Processing Service',
    description='A service for processing images',
    version='1.0.0',
    lifespan=lifespan,
)

app.include_router(auth_router, tags=['auth'])
app.include_router(image_router, tags=['image'])


@app.get('/')
def read_root():
    return {'message': 'Hello World!'}
