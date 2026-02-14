import factory
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from faker import Faker
from apps.goals.models import Goal
from .user_factory import UserFactory

fake = Faker()


class GoalFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Goal instances."""

    class Meta:
        model = Goal

    user = factory.SubFactory(UserFactory)
    name = factory.LazyAttribute(lambda _: "Goal - " + fake.word().capitalize())
    target_amount = factory.LazyAttribute(
        lambda _: Decimal(fake.random_int(min=100000, max=10000000))
    )
    current_amount = factory.LazyAttribute(
        lambda _: Decimal(fake.random_int(min=0, max=100000))
    )
    currency = "NGN"
    deadline = factory.LazyAttribute(
        lambda _: timezone.now().date() + timedelta(days=365)
    )
    goal_type = factory.Faker(
        "random_element", elements=["savings", "debt", "purchase"]
    )
    is_achieved = False
