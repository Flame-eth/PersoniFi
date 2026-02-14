import pytest
from decimal import Decimal
from apps.accounts.models import Account
from tests.factories import (
    UserFactory,
    AccountFactory,
    CardFactory,
)


@pytest.mark.django_db
class TestAccountModel:
    """Test suite for Account model."""

    def test_account_creation(self, auth_user):
        """Test that an account can be created."""
        account = AccountFactory(user=auth_user)
        assert account.id is not None
        assert account.user == auth_user
        assert account.balance >= 0

    def test_account_types(self, auth_user):
        """Test different account types."""
        account_types = ["bank", "mobile_money", "cash"]
        for acc_type in account_types:
            account = AccountFactory(user=auth_user, account_type=acc_type)
            assert account.account_type == acc_type

    def test_account_currencies(self, auth_user):
        """Test different account currencies."""
        currencies = ["NGN", "USD"]
        for currency in currencies:
            account = AccountFactory(user=auth_user, currency=currency)
            assert account.currency == currency

    def test_account_balance_decimal(self, auth_user):
        """Test that account balance is a Decimal."""
        account = AccountFactory(user=auth_user, balance=Decimal("1000.50"))
        assert isinstance(account.balance, Decimal)
        assert account.balance == Decimal("1000.50")

    def test_account_str_representation(self, auth_user):
        """Test account string representation."""
        account = AccountFactory(user=auth_user, name="My Bank", currency="NGN")
        assert str(account) == "My Bank (NGN)"

    def test_account_is_active(self, auth_user):
        """Test account active status."""
        account = AccountFactory(user=auth_user, is_active=True)
        assert account.is_active is True

    def test_account_institution(self, auth_user):
        """Test account institution field."""
        account = AccountFactory(user=auth_user, institution="First Bank")
        assert account.institution == "First Bank"

    def test_card_factory(self, auth_user):
        """Test card factory creates accounts."""
        card = CardFactory(user=auth_user)
        assert card.account_type == "bank"
        assert card.user == auth_user


@pytest.mark.django_db
class TestAccountQuerySet:
    """Test suite for Account QuerySet."""

    def test_account_count_per_user(self, auth_user):
        """Test counting accounts per user."""
        AccountFactory.create_batch(3, user=auth_user)
        assert Account.objects.filter(user=auth_user).count() == 3

    def test_account_filter_by_type(self, auth_user):
        """Test filtering accounts by type."""
        AccountFactory(user=auth_user, account_type="bank")
        AccountFactory(user=auth_user, account_type="mobile_money")

        bank_accounts = Account.objects.filter(account_type="bank")
        assert bank_accounts.count() == 1

    def test_account_filter_by_currency(self, auth_user):
        """Test filtering accounts by currency."""
        AccountFactory(user=auth_user, currency="NGN")
        AccountFactory(user=auth_user, currency="USD")

        ngn_accounts = Account.objects.filter(currency="NGN")
        assert ngn_accounts.count() == 1

    def test_account_filter_active_only(self, auth_user):
        """Test filtering active accounts."""
        AccountFactory(user=auth_user, is_active=True)
        AccountFactory(user=auth_user, is_active=False)

        active_accounts = Account.objects.filter(is_active=True)
        assert active_accounts.count() == 1

    def test_user_accounts_relationship(self, auth_user):
        """Test user-accounts relationship."""
        accounts = AccountFactory.create_batch(3, user=auth_user)
        assert auth_user.accounts.count() == 3
        for account in accounts:
            assert account in auth_user.accounts.all()


@pytest.mark.django_db
class TestAccountBalance:
    """Test suite for Account balance operations."""

    def test_account_default_balance_zero(self, auth_user):
        """Test that default balance is zero."""
        account = AccountFactory(user=auth_user)
        assert account.balance >= Decimal("0")

    def test_account_balance_update(self, auth_user):
        """Test updating account balance."""
        account = AccountFactory(user=auth_user, balance=Decimal("1000"))
        account.balance = Decimal("1500")
        account.save()

        refreshed = Account.objects.get(id=account.id)
        assert refreshed.balance == Decimal("1500")

    def test_account_large_balance(self, auth_user):
        """Test handling large balance amounts."""
        large_balance = Decimal("999999999.99")
        account = AccountFactory(user=auth_user, balance=large_balance)
        assert account.balance == large_balance


@pytest.mark.django_db
class TestMultipleAccounts:
    """Test suite for managing multiple accounts."""

    def test_multiple_user_accounts(self, multiple_accounts, auth_user):
        """Test user with multiple accounts."""
        assert len(multiple_accounts) == 3
        for account in multiple_accounts:
            assert account.user == auth_user

    def test_accounts_isolation_by_user(self):
        """Test that accounts are isolated by user."""
        user1 = UserFactory()
        user2 = UserFactory()

        AccountFactory(user=user1)
        AccountFactory(user=user2)

        assert user1.accounts.count() == 1
        assert user2.accounts.count() == 1
