import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.budgets.models import Budget, BudgetCategory
from tests.factories import (
    UserFactory,
    BudgetFactory,
    BudgetCategoryFactory,
    TransactionCategoryFactory,
)


@pytest.mark.django_db
class TestBudgetModel:
    """Test suite for Budget model."""

    def test_budget_creation(self, auth_user):
        """Test that a budget can be created."""
        budget = BudgetFactory(user=auth_user)
        assert budget.id is not None
        assert budget.user == auth_user
        assert budget.total_amount > 0

    def test_budget_date_range(self, auth_user):
        """Test budget date range."""
        today = timezone.now().date()
        start_date = today
        end_date = today + timedelta(days=30)

        budget = BudgetFactory(user=auth_user, start_date=start_date, end_date=end_date)
        assert budget.start_date == start_date
        assert budget.end_date == end_date

    def test_budget_total_amount_decimal(self, auth_user):
        """Test that total amount is decimal."""
        budget = BudgetFactory(user=auth_user, total_amount=Decimal("100000.50"))
        assert isinstance(budget.total_amount, Decimal)
        assert budget.total_amount == Decimal("100000.50")

    def test_budget_currency(self, auth_user):
        """Test budget currency."""
        budget = BudgetFactory(user=auth_user, currency="NGN")
        assert budget.currency == "NGN"

    def test_budget_active_by_default(self, auth_user):
        """Test budget is active by default."""
        budget = BudgetFactory(user=auth_user)
        assert budget.is_active is True

    def test_budget_str_representation(self, auth_user):
        """Test budget string representation."""
        budget = BudgetFactory(user=auth_user, name="Monthly Budget")
        assert str(budget) == "Monthly Budget"


@pytest.mark.django_db
class TestBudgetCategory:
    """Test suite for BudgetCategory."""

    def test_budget_category_creation(self, auth_user):
        """Test creating budget category."""
        budget = BudgetFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user, category_type="expense")

        budget_cat = BudgetCategoryFactory(budget=budget, category=category)
        assert budget_cat.budget == budget
        assert budget_cat.category == category

    def test_budget_category_allocated_amount(self, auth_user):
        """Test budget category allocated amount."""
        budget = BudgetFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)

        budget_cat = BudgetCategoryFactory(
            budget=budget, category=category, allocated_amount=Decimal("50000")
        )
        assert budget_cat.allocated_amount == Decimal("50000")

    def test_budget_category_alert_threshold(self, auth_user):
        """Test alert threshold."""
        budget = BudgetFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)

        budget_cat = BudgetCategoryFactory(
            budget=budget, category=category, alert_threshold=Decimal("0.8")
        )
        assert budget_cat.alert_threshold == Decimal("0.8")

    def test_budget_category_str_representation(self, auth_user):
        """Test budget category string representation."""
        budget = BudgetFactory(user=auth_user, name="Monthly Budget")
        category = TransactionCategoryFactory(user=auth_user, name="Food")

        budget_cat = BudgetCategoryFactory(budget=budget, category=category)
        assert "Monthly Budget" in str(budget_cat)
        assert "Food" in str(budget_cat)


@pytest.mark.django_db
class TestBudgetCategories:
    """Test suite for Budget categories relationship."""

    def test_budget_with_multiple_categories(self, budget_with_categories):
        """Test budget with multiple categories."""
        assert budget_with_categories.categories.count() == 2

    def test_add_category_to_budget(self, auth_user):
        """Test adding categories to budget."""
        budget = BudgetFactory(user=auth_user)
        category1 = TransactionCategoryFactory(user=auth_user)
        category2 = TransactionCategoryFactory(user=auth_user)

        BudgetCategoryFactory(budget=budget, category=category1)
        BudgetCategoryFactory(budget=budget, category=category2)

        assert budget.categories.count() == 2


@pytest.mark.django_db
class TestBudgetQuerySet:
    """Test suite for Budget QuerySet."""

    def test_budget_count_per_user(self, auth_user):
        """Test counting budgets per user."""
        BudgetFactory.create_batch(3, user=auth_user)
        assert Budget.objects.filter(user=auth_user).count() == 3

    def test_filter_active_budgets(self, auth_user):
        """Test filtering active budgets."""
        BudgetFactory(user=auth_user, is_active=True)
        BudgetFactory(user=auth_user, is_active=False)

        active = Budget.objects.filter(is_active=True)
        assert active.count() >= 1

    def test_filter_budgets_by_date_range(self, auth_user):
        """Test filtering budgets by date range."""
        today = timezone.now().date()
        start = today
        end = today + timedelta(days=30)

        budget = BudgetFactory(user=auth_user, start_date=start, end_date=end)

        filtered = Budget.objects.filter(start_date__lte=start, end_date__gte=end)
        assert budget in filtered

    def test_user_budgets_relationship(self, auth_user):
        """Test user budgets relationship."""
        budgets = BudgetFactory.create_batch(3, user=auth_user)
        assert auth_user.budgets.count() == 3
        for budget in budgets:
            assert budget in auth_user.budgets.all()


@pytest.mark.django_db
class TestBudgetIsolation:
    """Test suite for budget data isolation."""

    def test_budgets_isolated_by_user(self):
        """Test budgets are isolated by user."""
        user1 = UserFactory()
        user2 = UserFactory()

        BudgetFactory(user=user1)
        BudgetFactory(user=user2)

        assert user1.budgets.count() == 1
        assert user2.budgets.count() == 1
