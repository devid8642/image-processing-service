from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default=func.now()
    )


@table_registry.mapped_as_dataclass
class Image:
    __tablename__ = 'images'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    filename: Mapped[str]
    url: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    original_image_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('images.id'), default=None
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default=func.now()
    )
