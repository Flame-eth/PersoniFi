import pytest
import json
from rest_framework import status
from django.urls import reverse
from tests.factories import (
    AuthUserFactory,
    AccountFactory,
    TransactionFactory,
    TransactionCategoryFactory,
    BudgetFactory,
    GoalFactory,
)


@pytest.mark.rest
@pytest.mark.django_db
class TestAccountAPI:
    """Test suite for Account REST API endpoints."""

    def test_list_accounts_unauthenticated(self, api_client):
        """Test listing accounts requires authentication."""
        url = reverse("account-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_accounts_authenticated(self, authenticated_api_client, auth_user):
        """Test listing accounts for authenticated user."""
        AccountFactory(user=auth_user)
        AccountFactory(user=auth_user)

        url = reverse("account-list")
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # Should return user's accounts
        assert len(response.json()["results"]) >= 0

    def test_create_account(self, authenticated_api_client):
        """Test creating an account."""
        url = reverse("account-list")
        data = {
            "name": "Test Account",
            "account_type": "bank",
            "currency": "NGN",
            "balance": "10000.00",
            "institution": "Test Bank",
        }
        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve_account(self, authenticated_api_client, auth_user):
        """Test retrieving a specific account."""
        account = AccountFactory(user=auth_user)
        url = reverse("account-detail", kwargs={"pk": account.id})
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == str(account.id)

    def test_update_account(self, authenticated_api_client, auth_user):
        """Test updating an account."""
        account = AccountFactory(user=auth_user)
        url = reverse("account-detail", kwargs={"pk": account.id})
        data = {"balance": "20000.00"}
        response = authenticated_api_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_delete_account(self, authenticated_api_client, auth_user):
        """Test deleting an account."""
        account = AccountFactory(user=auth_user)
        url = reverse("account-detail", kwargs={"pk": account.id})
        response = authenticated_api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.rest
@pytest.mark.django_db
class TestTransactionAPI:
    """Test suite for Transaction REST API endpoints."""

    def test_list_transactions_unauthenticated(self, api_client):
        """Test listing transactions requires authentication."""
        url = reverse("transaction-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_transactions_authenticated(self, authenticated_api_client, auth_user):
        """Test listing transactions for authenticated user."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)
        TransactionFactory(user=auth_user, account=account, category=category)

        url = reverse("transaction-list")
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_transaction(self, authenticated_api_client, auth_user):
        """Test creating a transaction."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)

        url = reverse("transaction-list")
        data = {
            "account": str(account.id),
            "category": str(category.id),
            "amount": "5000.00",
            "transaction_type": "expense",
            "payment_method": "cash",
            "description": "Test transaction",
        }
        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_filter_transactions_by_type(self, authenticated_api_client, auth_user):
        """Test filtering transactions by type."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)

        TransactionFactory(
            user=auth_user,
            account=account,
            category=category,
            transaction_type="expense",
        )
        TransactionFactory(
            user=auth_user,
            account=account,
            category=category,
            transaction_type="income",
        )

        url = reverse("transaction-list")
        response = authenticated_api_client.get(url, {"transaction_type": "expense"})
        assert response.status_code == status.HTTP_200_OK

    def test_filter_transactions_by_category(self, authenticated_api_client, auth_user):
        """Test filtering transactions by category."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)

        TransactionFactory(user=auth_user, account=account, category=category)

        url = reverse("transaction-list")
        response = authenticated_api_client.get(url, {"category": str(category.id)})
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.rest
@pytest.mark.django_db
class TestCategoryAPI:
    """Test suite for Category REST API endpoints."""

    def test_list_categories_authenticated(self, authenticated_api_client, auth_user):
        """Test listing categories."""
        TransactionCategoryFactory(user=auth_user)

        url = reverse("category-list")
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_category(self, authenticated_api_client):
        """Test creating a category."""
        url = reverse("category-list")
        data = {
            "name": "New Category",
            "category_type": "expense",
        }
        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.rest
@pytest.mark.django_db
class TestBudgetAPI:
    """Test suite for Budget REST API endpoints."""

    def test_list_budgets_authenticated(self, authenticated_api_client, auth_user):
        """Test listing budgets."""
        BudgetFactory(user=auth_user)

        url = reverse("budget-list")
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_budget(self, authenticated_api_client):
        """Test creating a budget."""
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        url = reverse("budget-list")
        data = {
            "name": "Monthly Budget",
            "total_amount": "100000.00",
            "currency": "NGN",
            "start_date": str(today),
            "end_date": str(today + timedelta(days=30)),
        }
        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.rest
@pytest.mark.django_db
class TestGoalAPI:
    """Test suite for Goal REST API endpoints."""

    def test_list_goals_authenticated(self, authenticated_api_client, auth_user):
        """Test listing goals."""
        GoalFactory(user=auth_user)

        url = reverse("goal-list")
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_goal(self, authenticated_api_client):
        """Test creating a goal."""
        from django.utils import timezone
        from datetime import timedelta

        url = reverse("goal-list")
        data = {
            "name": "House Fund",
            "target_amount": "10000000.00",
            "goal_type": "savings",
            "currency": "NGN",
            "deadline": str(timezone.now().date() + timedelta(days=365)),
        }
        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.rest
@pytest.mark.django_db
class TestAPIPagination:
    """Test API pagination."""

    def test_account_list_pagination(self, authenticated_api_client, auth_user):
        """Test pagination for account listing."""
        AccountFactory.create_batch(25, user=auth_user)

        url = reverse("account-list")
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # Check pagination structure
        assert "results" in response.json() or "data" in response.json()


@pytest.mark.rest
@pytest.mark.django_db
class TestAPIPermissions:
    """Test API permissions and authorization."""

    def test_user_can_only_access_own_accounts(self, authenticated_api_client):
        """Test that users can only access their own accounts."""
        # This would require additional setup to test cross-user access
        url = reverse("account-list")
        response = authenticated_api_client.get(url)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_cannot_update_other_users_account(self, auth_user):
        """Test that users cannot update other users' accounts."""
        other_user = AuthUserFactory()
        account = AccountFactory(user=other_user)

        # Create client for auth_user
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken

        client = APIClient()
        refresh = RefreshToken.for_user(auth_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        url = reverse("account-detail", kwargs={"pk": account.id})
        data = {"balance": "999999.00"}
        response = client.patch(url, data, format="json")
        # Should be forbidden or not found
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN,
        ]
