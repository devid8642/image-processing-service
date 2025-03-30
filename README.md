# Image Processing Service

A service for processing images. This service allows users to upload images and apply various transformations such as resizing, cropping, rotating, and applying filters like grayscale and sepia. The transformations are processed asynchronously using Celery and RabbitMQ.

### Project Description
For a complete project overview, visit the [Roadmap](https://roadmap.sh/projects/image-processing-service).

---

## Features

- **Image Upload**: Upload images for processing.
- **Image Transformations**: Apply transformations such as resize, crop, rotate, grayscale, and sepia.
- **Asynchronous Processing**: Image transformations are processed asynchronously using **Celery** and **RabbitMQ**.

---

## Getting Started

These instructions will help you set up the project locally for development and testing.

### Prerequisites

- **Python 3.12+**
- **uv**: Environment management
- **RabbitMQ**: For Celery to work, RabbitMQ must be running.
- **Database**: SQLite (by default, but can be configured for other databases).

### Clone the Repository

```bash
git clone git@github.com:devid8642/image-processing-service.git
cd image-processing-service
```
### Setting Up the Environment
```bash
uv sync
```

### Set up the environment variables
```bash
cp env.example .env
```

### Database Migrations
```bash
alembic upgrade head
```

### Running RabbitMQ
```bash
docker run -d -p 5672:5672 -p 15672:15672 --name rabbitmq rabbitmq:management
```

### Running the Project
```bash
task run
```

In another terminal:

```bash
task celery
```

### Running Tests
```bash
task test
```

## Project Structure

- **image_processing_service/main.py**: The entry point for the FastAPI application.
- **image_processing_service/models.py**: SQLAlchemy models for the application (e.g., Image).
- **image_processing_service/services**: Business logic.
- **image_processing_service/tasks.py**: Celery tasks.
- **image_processing_service/celery.py**: Configuration for Celery and RabbitMQ.
- **image_processing_service/settings.py**: Configuration for the application (e.g., database URL, secret key).
- **image_processing_service/schemas/**: Pydantic schemas for validating data.
- **image_processing_service/uploads/**: Directory for storing uploaded images.
