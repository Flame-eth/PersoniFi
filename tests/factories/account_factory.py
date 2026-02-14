import factory
from decimal import Decimal
from faker import Faker
from apps.accounts.models import Account
from .user_factory import UserFactory

fake = Faker()


class AccountFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Account instances."""

    class Meta:
        model = Account
        django_get_or_create = ("user", "name")

    user = factory.SubFactory(UserFactory)
    name = factory.LazyAttribute(lambda _: fake.word().capitalize() + " Account")
    account_type = factory.Faker(
        "random_element", elements=["bank", "mobile_money", "cash"]
    )
    currency = factory.Faker("random_element", elements=["NGN", "USD"])
    balance = factory.LazyAttribute(
        lambda _: Decimal(fake.random_int(min=1000, max=1000000))
    )
    institution = factory.LazyAttribute(lambda _: fake.company())
    is_active = True


class CardFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Card instances."""

    class Meta:
        model = Account

    user = factory.SubFactory(UserFactory)
    name = factory.LazyAttribute(lambda _: fake.credit_card_provider())
    account_type = "bank"
    currency = "NGN"
    balance = factory.LazyAttribute(
        lambda _: Decimal(fake.random_int(min=5000, max=500000))
    )
    institution = factory.LazyAttribute(lambda _: fake.company())
    is_active = True
