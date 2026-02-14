import factory
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from faker import Faker
from apps.budgets.models import Budget, BudgetCategory
from apps.categories.models import Category
from .user_factory import UserFactory
from .transaction_factory import TransactionCategoryFactory

fake = Faker()


class BudgetFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Budget instances."""

    class Meta:
        model = Budget

    user = factory.SubFactory(UserFactory)
    name = factory.LazyAttribute(lambda _: "Budget - " + fake.word().capitalize())
    total_amount = factory.LazyAttribute(
        lambda _: Decimal(fake.random_int(min=50000, max=500000))
    )
    currency = "NGN"
    start_date = factory.LazyAttribute(lambda _: timezone.now().date())
    end_date = factory.LazyAttribute(
        lambda _: timezone.now().date() + timedelta(days=30)
    )
    is_active = True


class BudgetCategoryFactory(factory.django.DjangoModelFactory):
    """Factory for creating test BudgetCategory instances."""

    class Meta:
        model = BudgetCategory

    budget = factory.SubFactory(BudgetFactory)
    category = factory.SubFactory(
        TransactionCategoryFactory,
        user=factory.SelfAttribute("..budget.user"),
        category_type="expense",
    )
    allocated_amount = factory.LazyAttribute(
        lambda _: Decimal(fake.random_int(min=5000, max=100000))
    )
    alert_threshold = Decimal("0.8")
