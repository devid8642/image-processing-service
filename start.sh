#!/bin/sh
set -e
set -x

alembic upgrade head

fastapi run --workers 4 image_processing_service/main.py