from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from image_processing_service.models import User


@pytest.mark.asyncio
async def test_user(session: AsyncSession, mock_db_time: callable):
    with mock_db_time(model=User) as time:
        new_user = User(username='alice', password='secret')
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'alice'))

    assert asdict(user) == {
        'id': 1,
        'username': 'alice',
        'password': 'secret',
        'created_at': time,
    }
