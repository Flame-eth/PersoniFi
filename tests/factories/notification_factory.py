import factory
from faker import Faker
from apps.notifications.models import Notification
from .user_factory import UserFactory

fake = Faker()


class NotificationFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Notification instances."""

    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))
    message = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=200))
    is_read = False
