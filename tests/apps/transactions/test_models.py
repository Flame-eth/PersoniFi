import pytest
from decimal import Decimal
from django.utils import timezone
from apps.transactions.models import Transaction
from tests.factories import (
    UserFactory,
    AccountFactory,
    TransactionFactory,
    TransactionCategoryFactory,
)


@pytest.mark.django_db
class TestTransactionModel:
    """Test suite for Transaction model."""

    def test_transaction_creation(self, auth_user, account, category):
        """Test that a transaction can be created."""
        transaction = TransactionFactory(
            user=auth_user, account=account, category=category
        )
        assert transaction.id is not None
        assert transaction.user == auth_user
        assert transaction.account == account

    def test_transaction_types(self, auth_user, account):
        """Test different transaction types."""
        category = TransactionCategoryFactory(user=auth_user)

        for trans_type in ["income", "expense"]:
            transaction = TransactionFactory(
                user=auth_user,
                account=account,
                category=category,
                transaction_type=trans_type,
            )
            assert transaction.transaction_type == trans_type

    def test_transaction_payment_methods(self, auth_user, account, category):
        """Test different payment methods."""
        payment_methods = ["cash", "mobile_money", "bank_transfer", "card"]

        for method in payment_methods:
            transaction = TransactionFactory(
                user=auth_user,
                account=account,
                category=category,
                payment_method=method,
            )
            assert transaction.payment_method == method

    def test_transaction_amount_decimal(self, auth_user, account, category):
        """Test that transaction amount is a Decimal."""
        transaction = TransactionFactory(
            user=auth_user,
            account=account,
            category=category,
            amount=Decimal("5000.50"),
        )
        assert isinstance(transaction.amount, Decimal)
        assert transaction.amount == Decimal("5000.50")

    def test_transaction_date_default(self, auth_user, account, category):
        """Test that transaction date defaults to today."""
        transaction = TransactionFactory(
            user=auth_user, account=account, category=category
        )
        assert transaction.date == timezone.now().date()

    def test_transaction_str_representation(self, auth_user, account, category):
        """Test transaction string representation."""
        transaction = TransactionFactory(
            user=auth_user,
            account=account,
            category=category,
            transaction_type="expense",
            amount=Decimal("1000"),
        )
        assert "expense" in str(transaction)
        assert "1000" in str(transaction)

    def test_transaction_description_optional(self, auth_user, account, category):
        """Test transaction description is optional."""
        transaction = TransactionFactory(
            user=auth_user, account=account, category=category, description=""
        )
        assert transaction.description == ""

    def test_transaction_notes_optional(self, auth_user, account, category):
        """Test transaction notes are optional."""
        transaction = TransactionFactory(
            user=auth_user, account=account, category=category, notes=""
        )
        assert transaction.notes == ""


@pytest.mark.django_db
class TestTransactionCategory:
    """Test suite for TransactionCategory."""

    def test_category_creation(self, auth_user):
        """Test that a category can be created."""
        category = TransactionCategoryFactory(user=auth_user)
        assert category.id is not None
        assert category.user == auth_user

    def test_category_types(self, auth_user):
        """Test different category types."""
        for cat_type in ["income", "expense"]:
            category = TransactionCategoryFactory(
                user=auth_user, category_type=cat_type
            )
            assert category.category_type == cat_type

    def test_category_active_by_default(self, auth_user):
        """Test that categories are active by default."""
        category = TransactionCategoryFactory(user=auth_user)
        assert category.is_active is True

    def test_category_hierarchical_structure(self, auth_user):
        """Test hierarchical category structure."""
        parent_category = TransactionCategoryFactory(user=auth_user)
        child_category = TransactionCategoryFactory(
            user=auth_user, parent=parent_category
        )

        assert child_category.parent == parent_category
        assert child_category in parent_category.children.all()


@pytest.mark.django_db
class TestTransactionQuerySet:
    """Test suite for Transaction QuerySet."""

    def test_transaction_count(self, auth_user, account):
        """Test counting transactions."""
        category = TransactionCategoryFactory(user=auth_user)
        TransactionFactory.create_batch(
            5, user=auth_user, account=account, category=category
        )
        assert Transaction.objects.filter(user=auth_user).count() == 5

    def test_filter_transactions_by_type(self, multiple_transactions, auth_user):
        """Test filtering transactions by type."""
        # Create specific transactions
        category = TransactionCategoryFactory(user=auth_user)
        account = AccountFactory(user=auth_user)

        TransactionFactory(
            user=auth_user,
            account=account,
            category=category,
            transaction_type="income",
        )
        TransactionFactory(
            user=auth_user,
            account=account,
            category=category,
            transaction_type="expense",
        )

        income = Transaction.objects.filter(transaction_type="income")
        assert income.count() >= 1

    def test_filter_transactions_by_category(self, auth_user, account):
        """Test filtering transactions by category."""
        category1 = TransactionCategoryFactory(user=auth_user)
        category2 = TransactionCategoryFactory(user=auth_user)

        TransactionFactory.create_batch(
            3, user=auth_user, account=account, category=category1
        )
        TransactionFactory.create_batch(
            2, user=auth_user, account=account, category=category2
        )

        cat1_transactions = Transaction.objects.filter(category=category1)
        cat2_transactions = Transaction.objects.filter(category=category2)

        assert cat1_transactions.count() == 3
        assert cat2_transactions.count() == 2

    def test_transactions_per_account(self, auth_user):
        """Test transactions per account."""
        account1 = AccountFactory(user=auth_user)
        account2 = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)

        TransactionFactory.create_batch(
            3, user=auth_user, account=account1, category=category
        )
        TransactionFactory.create_batch(
            2, user=auth_user, account=account2, category=category
        )

        assert account1.transactions.count() == 3
        assert account2.transactions.count() == 2


@pytest.mark.django_db
class TestTransactionAmount:
    """Test suite for Transaction amount operations."""

    def test_transaction_zero_amount(self, auth_user, account, category):
        """Test creating transaction with zero amount."""
        transaction = TransactionFactory(
            user=auth_user, account=account, category=category, amount=Decimal("0")
        )
        assert transaction.amount == Decimal("0")

    def test_transaction_large_amount(self, auth_user, account, category):
        """Test transaction with large amount."""
        large_amount = Decimal("999999999.99")
        transaction = TransactionFactory(
            user=auth_user, account=account, category=category, amount=large_amount
        )
        assert transaction.amount == large_amount

    def test_transaction_with_cents(self, auth_user, account, category):
        """Test transaction with cents precision."""
        amount = Decimal("1500.75")
        transaction = TransactionFactory(
            user=auth_user, account=account, category=category, amount=amount
        )
        assert transaction.amount == amount


@pytest.mark.django_db
class TestTransactionIsolation:
    """Test suite for transaction data isolation."""

    def test_transactions_isolated_by_user(self):
        """Test transactions isolated between users."""
        user1 = UserFactory()
        user2 = UserFactory()

        account1 = AccountFactory(user=user1)
        account2 = AccountFactory(user=user2)

        category1 = TransactionCategoryFactory(user=user1)
        category2 = TransactionCategoryFactory(user=user2)

        TransactionFactory(user=user1, account=account1, category=category1)
        TransactionFactory(user=user2, account=account2, category=category2)

        assert user1.transactions.count() == 1
        assert user2.transactions.count() == 1
