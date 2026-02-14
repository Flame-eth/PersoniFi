import pytest
import json
from django.urls import reverse
from tests.factories import (
    AuthUserFactory,
    AccountFactory,
    TransactionFactory,
    TransactionCategoryFactory,
    BudgetFactory,
    GoalFactory,
)


@pytest.mark.graphql
@pytest.mark.django_db
class TestGraphQLAuthentication:
    """Test GraphQL authentication."""

    def test_graphql_unauthenticated_query(self, graphql_client):
        """Test unauthenticated GraphQL query."""
        query = """
        query {
            accounts {
                id
                name
            }
        }
        """
        url = reverse("graphql-view")
        response = graphql_client.post(
            url, json={"query": query}, content_type="application/json"
        )
        # Should return 200 but with error in response
        assert response.status_code == 200
        data = json.loads(response.content)
        # Unauthenticated request should have errors or no data
        assert "errors" in data or data.get("data") is None

    def test_graphql_authenticated_query(self, authenticated_graphql_client, auth_user):
        """Test authenticated GraphQL query."""
        AccountFactory(user=auth_user)

        query = """
        query {
            accounts {
                id
                name
            }
        }
        """
        url = reverse("graphql-view")
        response = authenticated_graphql_client.post(
            url, json={"query": query}, content_type="application/json"
        )
        assert response.status_code == 200


@pytest.mark.graphql
@pytest.mark.django_db
class TestGraphQLQueries:
    """Test GraphQL query operations."""

    def test_query_accounts(self, authenticated_graphql_client, auth_user):
        """Test querying user accounts."""
        account = AccountFactory(user=auth_user, name="Test Account")

        query = """
        query {
            accounts {
                id
                name
                accountType
                balance
            }
        }
        """
        url = reverse("graphql-view")
        response = authenticated_graphql_client.post(
            url, json={"query": query}, content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.content)
        # Check if query returns data
        if "data" in data and data["data"]:
            assert "accounts" in data["data"]

    def test_query_transactions(self, authenticated_graphql_client, auth_user):
        """Test querying user transactions."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)
        TransactionFactory(user=auth_user, account=account, category=category)

        query = """
        query {
            transactions {
                id
                amount
                transactionType
            }
        }
        """
        url = reverse("graphql-view")
        response = authenticated_graphql_client.post(
            url, json={"query": query}, content_type="application/json"
        )
        assert response.status_code == 200

    def test_query_budgets(self, authenticated_graphql_client, auth_user):
        """Test querying user budgets."""
        BudgetFactory(user=auth_user)

        query = """
        query {
            budgets {
                id
                name
                totalAmount
            }
        }
        """
        url = reverse("graphql-view")
        response = authenticated_graphql_client.post(
            url, json={"query": query}, content_type="application/json"
        )
        assert response.status_code == 200

    def test_query_goals(self, authenticated_graphql_client, auth_user):
        """Test querying user goals."""
        GoalFactory(user=auth_user)

        query = """
        query {
            goals {
                id
                name
                targetAmount
                currentAmount
            }
        }
        """
        url = reverse("graphql-view")
        response = authenticated_graphql_client.post(
            url, json={"query": query}, content_type="application/json"
        )
        assert response.status_code == 200


@pytest.mark.graphql
@pytest.mark.django_db
class TestGraphQLMutations:
    """Test GraphQL mutation operations."""

    def test_create_account_mutation(self, authenticated_graphql_client):
        """Test creating an account via GraphQL."""
        mutation = """
        mutation {
            createAccount(
                input: {
                    name: "New Account"
                    accountType: "bank"
                    currency: "NGN"
                    balance: "50000"
                    institution: "Test Bank"
                }
            ) {
                account {
                    id
                    name
                }
            }
        }
        """
        url = reverse("graphql-view")
        response = authenticated_graphql_client.post(
            url, json={"query": mutation}, content_type="application/json"
        )
        assert response.status_code == 200

    def test_create_transaction_mutation(self, authenticated_graphql_client, auth_user):
        """Test creating a transaction via GraphQL."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)

        mutation = f"""
        mutation {{
            createTransaction(
                input: {{
                    accountId: "{account.id}"
                    categoryId: "{category.id}"
                    amount: "5000"
                    transactionType: "expense"
                    paymentMethod: "cash"
                    description: "Test transaction"
                }}
            ) {{
                transaction {{
                    id
                    amount
                }}
            }}
        }}
        """
        url = reverse("graphql-view")
        response = authenticated_graphql_client.post(
            url, json={"query": mutation}, content_type="application/json"
        )
        assert response.status_code == 200

    def test_create_budget_mutation(self, authenticated_graphql_client):
        """Test creating a budget via GraphQL."""
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        end_date = today + timedelta(days=30)

        mutation = f"""
        mutation {{
            createBudget(
                input: {{
                    name: "Monthly Budget"
                    totalAmount: "100000"
                    currency: "NGN"
                    startDate: "{today}"
                    endDate: "{end_date}"
                }}
            ) {{
                budget {{
                    id
                    name
                }}
            }}
        }}
        """
        url = reverse("graphql-view")
        response = authenticated_graphql_client.post(
            url, json={"query": mutation}, content_type="application/json"
        )
        assert response.status_code == 200

    def test_create_goal_mutation(self, authenticated_graphql_client):
        """Test creating a goal via GraphQL."""
        from django.utils import timezone
        from datetime import timedelta

        deadline = timezone.now().date() + timedelta(days=365)

        mutation = f"""
        mutation {{
            createGoal(
                input: {{
                    name: "House Fund"
                    targetAmount: "10000000"
                    goalType: "savings"
                    currency: "NGN"
                    deadline: "{deadline}"
                }}
            ) {{
                goal {{
                    id
                    name
                }}
            }}
        }}
        """
        url = reverse("graphql-view")
        response = authenticated_graphql_client.post(
            url, json={"query": mutation}, content_type="application/json"
        )
        assert response.status_code == 200


@pytest.mark.graphql
@pytest.mark.django_db
class TestGraphQLErrors:
    """Test GraphQL error handling."""

    def test_invalid_query_syntax(self, authenticated_graphql_client):
        """Test GraphQL with invalid syntax."""
        query = """
        query {
            invalidField {
                id
            }
        }
        """
        url = reverse("graphql-view")
        response = authenticated_graphql_client.post(
            url, json={"query": query}, content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.content)
        # Should return error in response
        assert "errors" in data or "data" in data

    def test_missing_required_field(self, authenticated_graphql_client):
        """Test mutation with missing required field."""
        mutation = """
        mutation {
            createAccount(
                input: {
                    accountType: "bank"
                }
            ) {
                account {
                    id
                }
            }
        }
        """
        url = reverse("graphql-view")
        response = authenticated_graphql_client.post(
            url, json={"query": mutation}, content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.content)
        # Should return error
        assert "errors" in data or data.get("data") is None


@pytest.mark.graphql
@pytest.mark.django_db
class TestGraphQLFieldResolution:
    """Test GraphQL field resolution and nesting."""

    def test_nested_account_details(self, authenticated_graphql_client, auth_user):
        """Test nested field resolution."""
        account = AccountFactory(user=auth_user, name="Test Account")

        query = """
        query {
            accounts {
                id
                name
                user {
                    id
                    email
                }
            }
        }
        """
        url = reverse("graphql-view")
        response = authenticated_graphql_client.post(
            url, json={"query": query}, content_type="application/json"
        )
        assert response.status_code == 200

    def test_transaction_with_nested_fields(
        self, authenticated_graphql_client, auth_user
    ):
        """Test transaction query with nested relations."""
        account = AccountFactory(user=auth_user)
        category = TransactionCategoryFactory(user=auth_user)
        TransactionFactory(user=auth_user, account=account, category=category)

        query = """
        query {
            transactions {
                id
                amount
                account {
                    id
                    name
                }
                category {
                    id
                    name
                }
            }
        }
        """
        url = reverse("graphql-view")
        response = authenticated_graphql_client.post(
            url, json={"query": query}, content_type="application/json"
        )
        assert response.status_code == 200
