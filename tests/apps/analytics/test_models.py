import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.analytics.models import FinancialSnapshot
from tests.factories import (
    UserFactory,
    AccountFactory,
    TransactionFactory,
    TransactionCategoryFactory,
)


@pytest.fixture
def financial_snapshot_factories():
    """Factory for creating FinancialSnapshot instances."""
    from tests.factories import UserFactory

    def create_snapshot(date=None, income=Decimal("0"), expense=Decimal("0")):
        if date is None:
            date = timezone.now().date()

        return FinancialSnapshot.objects.create(
            created_for_date=date,
            total_income=income,
            total_expense=expense,
        )

    return create_snapshot


@pytest.mark.django_db
class TestFinancialSnapshot:
    """Test suite for FinancialSnapshot model."""

    def test_snapshot_creation(self):
        """Test creating a financial snapshot."""
        snapshot = FinancialSnapshot.objects.create(
            created_for_date=timezone.now().date(),
            total_income=Decimal("50000"),
            total_expense=Decimal("30000"),
        )
        assert snapshot.id is not None
        assert snapshot.total_income == Decimal("50000")
        assert snapshot.total_expense == Decimal("30000")

    def test_snapshot_str_representation(self):
        """Test snapshot string representation."""
        date = timezone.now().date()
        snapshot = FinancialSnapshot.objects.create(
            created_for_date=date,
            total_income=Decimal("50000"),
            total_expense=Decimal("30000"),
        )
        assert str(snapshot) == str(date)

    def test_snapshot_date_field(self):
        """Test snapshot date field."""
        date = timezone.now().date()
        snapshot = FinancialSnapshot.objects.create(
            created_for_date=date,
            total_income=Decimal("50000"),
            total_expense=Decimal("30000"),
        )
        assert snapshot.created_for_date == date

    def test_snapshot_default_amounts(self):
        """Test snapshot default amounts are zero."""
        snapshot = FinancialSnapshot.objects.create(
            created_for_date=timezone.now().date()
        )
        assert snapshot.total_income == Decimal("0")
        assert snapshot.total_expense == Decimal("0")


@pytest.mark.django_db
class TestAnalyticsCalculations:
    """Test suite for analytics calculations."""

    def test_net_income_calculation(self):
        """Test calculating net income from snapshots."""
        income = Decimal("100000")
        expense = Decimal("60000")

        snapshot = FinancialSnapshot.objects.create(
            created_for_date=timezone.now().date(),
            total_income=income,
            total_expense=expense,
        )

        net = snapshot.total_income - snapshot.total_expense
        assert net == Decimal("40000")

    def test_expense_ratio(self):
        """Test calculating expense ratio."""
        income = Decimal("100000")
        expense = Decimal("30000")

        snapshot = FinancialSnapshot.objects.create(
            created_for_date=timezone.now().date(),
            total_income=income,
            total_expense=expense,
        )

        ratio = (snapshot.total_expense / snapshot.total_income) * 100
        assert ratio == Decimal("30")

    def test_savings_rate(self):
        """Test calculating savings rate."""
        income = Decimal("100000")
        expense = Decimal("70000")

        snapshot = FinancialSnapshot.objects.create(
            created_for_date=timezone.now().date(),
            total_income=income,
            total_expense=expense,
        )

        savings = income - expense
        savings_rate = (savings / income) * 100
        assert savings_rate == Decimal("30")


@pytest.mark.django_db
class TestSnapshotQuerySet:
    """Test suite for FinancialSnapshot QuerySet."""

    def test_snapshot_count(self):
        """Test counting snapshots."""
        today = timezone.now().date()
        for i in range(5):
            FinancialSnapshot.objects.create(
                created_for_date=today - timedelta(days=i),
                total_income=Decimal("50000"),
                total_expense=Decimal("30000"),
            )
        assert FinancialSnapshot.objects.count() == 5

    def test_filter_snapshots_by_date(self):
        """Test filtering snapshots by date."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        FinancialSnapshot.objects.create(
            created_for_date=today,
            total_income=Decimal("50000"),
        )
        FinancialSnapshot.objects.create(
            created_for_date=yesterday,
            total_income=Decimal("40000"),
        )

        today_snapshot = FinancialSnapshot.objects.filter(created_for_date=today)
        assert today_snapshot.count() == 1

    def test_filter_snapshots_by_date_range(self):
        """Test filtering snapshots by date range."""
        today = timezone.now().date()
        start_date = today - timedelta(days=7)

        for i in range(10):
            FinancialSnapshot.objects.create(
                created_for_date=today - timedelta(days=i),
                total_income=Decimal("50000"),
            )

        recent = FinancialSnapshot.objects.filter(
            created_for_date__gte=start_date, created_for_date__lte=today
        )
        assert recent.count() > 0

    def test_order_snapshots_chronologically(self):
        """Test ordering snapshots chronologically."""
        today = timezone.now().date()

        FinancialSnapshot.objects.create(created_for_date=today)
        FinancialSnapshot.objects.create(created_for_date=today - timedelta(days=1))
        FinancialSnapshot.objects.create(created_for_date=today - timedelta(days=2))

        ordered = FinancialSnapshot.objects.order_by("created_for_date")
        dates = [snap.created_for_date for snap in ordered]

        assert dates == sorted(dates)


@pytest.mark.django_db
class TestAnalyticsWithTransactions:
    """Test suite for analytics with actual transaction data."""

    def test_income_from_transactions(self, auth_user):
        """Test calculating income from transactions."""
        account = AccountFactory(user=auth_user)
        income_category = TransactionCategoryFactory(
            user=auth_user, category_type="income"
        )

        # Create income transactions
        TransactionFactory(
            user=auth_user,
            account=account,
            category=income_category,
            transaction_type="income",
            amount=Decimal("50000"),
        )
        TransactionFactory(
            user=auth_user,
            account=account,
            category=income_category,
            transaction_type="income",
            amount=Decimal("30000"),
        )

        total_income = auth_user.transactions.filter(
            transaction_type="income"
        ).aggregate(total=models.Sum("amount"))["total"]

        assert total_income == Decimal("80000")

    def test_expense_from_transactions(self, auth_user):
        """Test calculating expenses from transactions."""
        account = AccountFactory(user=auth_user)
        expense_category = TransactionCategoryFactory(
            user=auth_user, category_type="expense"
        )

        # Create expense transactions
        TransactionFactory(
            user=auth_user,
            account=account,
            category=expense_category,
            transaction_type="expense",
            amount=Decimal("20000"),
        )
        TransactionFactory(
            user=auth_user,
            account=account,
            category=expense_category,
            transaction_type="expense",
            amount=Decimal("15000"),
        )

        total_expense = auth_user.transactions.filter(
            transaction_type="expense"
        ).aggregate(total=models.Sum("amount"))["total"]

        assert total_expense == Decimal("35000")


@pytest.mark.django_db
class TestSnapshotTimestamps:
    """Test suite for snapshot timestamps."""

    def test_snapshot_created_timestamp(self):
        """Test snapshot creation timestamp."""
        snapshot = FinancialSnapshot.objects.create(
            created_for_date=timezone.now().date()
        )
        assert snapshot.created_at is not None

    def test_snapshot_updated_timestamp(self):
        """Test snapshot updated timestamp."""
        snapshot = FinancialSnapshot.objects.create(
            created_for_date=timezone.now().date()
        )
        original_updated = snapshot.updated_at

        # Update snapshot
        snapshot.total_income = Decimal("100000")
        snapshot.save()

        assert snapshot.updated_at >= original_updated


# Import models for aggregation
from django.db import models
