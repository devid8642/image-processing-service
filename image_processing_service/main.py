from fastapi import FastAPI

from image_processing_service.routers.auth_router import auth_router

app = FastAPI()

app.include_router(auth_router, tags=['auth'])


@app.get('/')
def read_root():
    return {'message': 'Hello World!'}
