import factory
from decimal import Decimal
from django.utils import timezone
from faker import Faker
from apps.transactions.models import Transaction
from apps.categories.models import Category
from .user_factory import UserFactory
from .account_factory import AccountFactory

fake = Faker()


class TransactionCategoryFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Category instances."""

    class Meta:
        model = Category

    user = factory.SubFactory(UserFactory)
    name = factory.LazyAttribute(lambda _: fake.word().capitalize())
    category_type = factory.Faker("random_element", elements=["income", "expense"])
    is_active = True
    is_system = False


class TransactionFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Transaction instances."""

    class Meta:
        model = Transaction

    user = factory.SubFactory(UserFactory)
    account = factory.SubFactory(AccountFactory, user=factory.SelfAttribute("..user"))
    category = factory.SubFactory(
        TransactionCategoryFactory, user=factory.SelfAttribute("..user")
    )
    amount = factory.LazyAttribute(
        lambda _: Decimal(fake.random_int(min=100, max=100000))
    )
    currency = "NGN"
    transaction_type = factory.Faker("random_element", elements=["income", "expense"])
    date = factory.LazyAttribute(lambda _: timezone.now().date())
    description = factory.LazyAttribute(lambda _: fake.sentence(nb_words=6))
    notes = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=100))
    payment_method = factory.Faker(
        "random_element", elements=["cash", "mobile_money", "bank_transfer", "card"]
    )
