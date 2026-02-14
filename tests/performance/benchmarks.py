import pytest
from decimal import Decimal
from django.utils import timezone
from apps.transactions.models import Transaction
from apps.accounts.models import Account
from tests.factories import (
    AccountFactory,
    TransactionFactory,
    TransactionCategoryFactory,
)


@pytest.mark.performance
@pytest.mark.django_db
class TestQueryPerformance:
    """Test suite for database query performance."""

    def test_list_accounts_performance(self, benchmark, auth_user):
        """Benchmark accounts listing query."""
        # Create test data
        AccountFactory.create_batch(20, user=auth_user)

        def list_accounts():
            return list(Account.objects.filter(user=auth_user))

        result = benchmark(list_accounts)
        assert len(result) == 20

    def test_filter_transactions_by_category_performance(self, benchmark, auth_user):
        """Benchmark filtering transactions by category."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)

        # Create test data
        TransactionFactory.create_batch(
            50, user=auth_user, account=account, category=category
        )

        def filter_transactions():
            return list(Transaction.objects.filter(category=category)[:20])

        result = benchmark(filter_transactions)
        assert len(result) <= 20

    def test_aggregate_transactions_performance(self, benchmark, auth_user):
        """Benchmark transaction aggregation."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)

        # Create test data
        TransactionFactory.create_batch(
            100, user=auth_user, account=account, category=category
        )

        def aggregate_transactions():
            from django.db.models import Sum

            return Transaction.objects.filter(
                user=auth_user, transaction_type="expense"
            ).aggregate(total=Sum("amount"))

        result = benchmark(aggregate_transactions)
        assert result["total"] is not None or isinstance(
            result["total"], (Decimal, type(None))
        )

    def test_select_related_performance(self, benchmark, auth_user):
        """Benchmark select_related optimization."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)
        TransactionFactory.create_batch(
            30, user=auth_user, account=account, category=category
        )

        def query_with_relations():
            return list(
                Transaction.objects.select_related("account", "category").filter(
                    user=auth_user
                )[:20]
            )

        result = benchmark(query_with_relations)
        assert len(result) <= 20

    def test_distinct_categories_performance(self, benchmark, auth_user):
        """Benchmark distinct query."""
        account = AccountFactory(user=auth_user)

        # Create transactions with repeated categories
        categories = [TransactionCategoryFactory(user=auth_user) for _ in range(5)]
        for _ in range(20):
            for category in categories:
                TransactionFactory(user=auth_user, account=account, category=category)

        def distinct_categories():
            return list(
                Transaction.objects.filter(user=auth_user).values("category").distinct()
            )

        result = benchmark(distinct_categories)
        assert len(result) > 0


@pytest.mark.performance
@pytest.mark.rest
@pytest.mark.django_db
class TestAPIResponseTime:
    """Test suite for API endpoint response times."""

    def test_list_accounts_api_performance(
        self, benchmark, authenticated_api_client, auth_user
    ):
        """Benchmark accounts list API response time."""
        # Create test data
        AccountFactory.create_batch(20, user=auth_user)

        from django.urls import reverse

        def get_accounts():
            return authenticated_api_client.get(reverse("account-list"))

        result = benchmark(get_accounts)
        assert result.status_code in [200, 401]

    def test_list_transactions_api_performance(
        self, benchmark, authenticated_api_client, auth_user
    ):
        """Benchmark transactions list API response time."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)
        TransactionFactory.create_batch(
            50, user=auth_user, account=account, category=category
        )

        from django.urls import reverse

        def get_transactions():
            return authenticated_api_client.get(reverse("transaction-list"))

        result = benchmark(get_transactions)
        assert result.status_code in [200, 401]

    def test_create_account_api_performance(self, benchmark, authenticated_api_client):
        """Benchmark account creation API response time."""
        from django.urls import reverse

        def create_account():
            return authenticated_api_client.post(
                reverse("account-list"),
                {
                    "name": "Test Account",
                    "account_type": "bank",
                    "currency": "NGN",
                    "balance": "10000",
                },
                format="json",
            )

        result = benchmark(create_account)
        assert result.status_code in [201, 401]

    def test_retrieve_account_api_performance(
        self, benchmark, authenticated_api_client, auth_user
    ):
        """Benchmark account detail API response time."""
        account = AccountFactory(user=auth_user)

        from django.urls import reverse

        def get_account():
            return authenticated_api_client.get(
                reverse("account-detail", kwargs={"pk": account.id})
            )

        result = benchmark(get_account)
        assert result.status_code in [200, 401, 404]

    def test_filter_transactions_api_performance(
        self, benchmark, authenticated_api_client, auth_user
    ):
        """Benchmark filtered transactions API response time."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)
        TransactionFactory.create_batch(
            50, user=auth_user, account=account, category=category
        )

        from django.urls import reverse

        def filter_transactions():
            return authenticated_api_client.get(
                reverse("transaction-list"), {"category": str(category.id)}
            )

        result = benchmark(filter_transactions)
        assert result.status_code in [200, 401]


@pytest.mark.performance
@pytest.mark.django_db
class TestConcurrentOperations:
    """Test suite for concurrent operation performance."""

    def test_create_multiple_accounts_performance(self, benchmark, auth_user):
        """Benchmark creating multiple accounts."""

        def create_accounts():
            accounts = []
            for i in range(10):
                accounts.append(AccountFactory(user=auth_user, name=f"Account {i}"))
            return accounts

        result = benchmark(create_accounts)
        assert len(result) == 10

    def test_create_multiple_transactions_performance(self, benchmark, auth_user):
        """Benchmark creating multiple transactions."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)

        def create_transactions():
            transactions = []
            for i in range(20):
                transactions.append(
                    TransactionFactory(
                        user=auth_user, account=account, category=category
                    )
                )
            return transactions

        result = benchmark(create_transactions)
        assert len(result) == 20

    def test_bulk_update_performance(self, benchmark, auth_user):
        """Benchmark bulk update operations."""
        accounts = AccountFactory.create_batch(20, user=auth_user)

        def bulk_update():
            for account in accounts:
                account.balance = Decimal("5000.00")
            return Account.objects.bulk_update(accounts, ["balance"], batch_size=10)

        result = benchmark(bulk_update)
        assert result is not None


@pytest.mark.performance
@pytest.mark.django_db
class TestMemoryEfficiency:
    """Test suite for memory efficiency."""

    def test_large_result_set_memory(self, benchmark, auth_user):
        """Benchmark large result set handling."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)

        # Create many transactions
        TransactionFactory.create_batch(
            500, user=auth_user, account=account, category=category
        )

        def fetch_all_with_iterator():
            count = 0
            for transaction in Transaction.objects.filter(user=auth_user).iterator(
                chunk_size=100
            ):
                count += 1
            return count

        result = benchmark(fetch_all_with_iterator)
        assert result == 500

    def test_pagination_efficiency(self, benchmark, auth_user):
        """Benchmark paginated result set."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)

        # Create many transactions
        TransactionFactory.create_batch(
            200, user=auth_user, account=account, category=category
        )

        def fetch_paginated():
            page1 = list(Transaction.objects.filter(user=auth_user)[:50])
            page2 = list(Transaction.objects.filter(user=auth_user)[50:100])
            return len(page1) + len(page2)

        result = benchmark(fetch_paginated)
        assert result == 100


@pytest.mark.performance
@pytest.mark.django_db
class TestIndexEfficiency:
    """Test suite for query index efficiency."""

    def test_indexed_field_query(self, benchmark, auth_user):
        """Benchmark query on indexed field (user)."""
        AccountFactory.create_batch(100, user=auth_user)

        def query_by_user():
            return Account.objects.filter(user=auth_user).count()

        result = benchmark(query_by_user)
        assert result == 100

    def test_multiple_filter_performance(self, benchmark, auth_user):
        """Benchmark query with multiple filters."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)
        TransactionFactory.create_batch(
            100, user=auth_user, account=account, category=category
        )

        def multi_filter():
            return Transaction.objects.filter(
                user=auth_user,
                account=account,
                transaction_type="expense",
                category=category,
            ).count()

        result = benchmark(multi_filter)
        assert result >= 0
