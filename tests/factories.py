import factory

from image_processing_service.models import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
