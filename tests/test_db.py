from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from image_processing_service.models import User


def test_user(session: Session, mock_db_time: callable):
    with mock_db_time(model=User) as time:
        new_user = User(username='alice', password='secret')
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == 'alice'))

    assert asdict(user) == {
        'id': 1,
        'username': 'alice',
        'password': 'secret',
        'created_at': time,
    }
