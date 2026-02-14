import os
import django
import pytest
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.testing")
django.setup()

from tests.factories import (
    UserFactory,
    AuthUserFactory,
    AccountFactory,
    TransactionFactory,
    TransactionCategoryFactory,
    BudgetFactory,
    BudgetCategoryFactory,
    GoalFactory,
    NotificationFactory,
)


# ============================================================================
# SESSION FIXTURES - Database and Transactional Setup
# ============================================================================


@pytest.fixture(scope="session")
def django_db_setup():
    """Configure Django database for tests."""
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }


# ============================================================================
# USER FIXTURES
# ============================================================================


@pytest.fixture
def user(db):
    """Create a basic test user."""
    return UserFactory()


@pytest.fixture
def auth_user(db):
    """Create an authenticated user with password set."""
    user = AuthUserFactory()
    user.set_password("testpass123")
    user.save()
    return user


@pytest.fixture
def auth_user_with_data(db):
    """Create an authenticated user with associated test data."""
    user = AuthUserFactory()
    user.set_password("testpass123")
    user.save()

    # Create related test data
    AccountFactory(user=user)
    TransactionCategoryFactory(user=user)
    BudgetFactory(user=user)
    GoalFactory(user=user)
    NotificationFactory(user=user)

    return user


@pytest.fixture
def multiple_users(db):
    """Create multiple test users."""
    return [AuthUserFactory() for _ in range(3)]


# ============================================================================
# ACCOUNT FIXTURES
# ============================================================================


@pytest.fixture
def account(db, auth_user):
    """Create a test account for the authenticated user."""
    return AccountFactory(user=auth_user)


@pytest.fixture
def multiple_accounts(db, auth_user):
    """Create multiple test accounts for the authenticated user."""
    return [
        AccountFactory(user=auth_user, account_type="bank"),
        AccountFactory(user=auth_user, account_type="mobile_money"),
        AccountFactory(user=auth_user, account_type="cash"),
    ]


# ============================================================================
# TRANSACTION FIXTURES
# ============================================================================


@pytest.fixture
def category(db, auth_user):
    """Create a test transaction category."""
    return TransactionCategoryFactory(user=auth_user)


@pytest.fixture
def transaction(db, auth_user, account, category):
    """Create a test transaction."""
    return TransactionFactory(
        user=auth_user, account=account, category=category, transaction_type="expense"
    )


@pytest.fixture
def multiple_transactions(db, auth_user, account):
    """Create multiple test transactions."""
    category = TransactionCategoryFactory(user=auth_user)
    return [
        TransactionFactory(user=auth_user, account=account, category=category)
        for _ in range(5)
    ]


# ============================================================================
# BUDGET FIXTURES
# ============================================================================


@pytest.fixture
def budget(db, auth_user):
    """Create a test budget."""
    return BudgetFactory(user=auth_user)


@pytest.fixture
def budget_with_categories(db, auth_user):
    """Create a budget with allocated categories."""
    budget = BudgetFactory(user=auth_user)
    category1 = TransactionCategoryFactory(user=auth_user, category_type="expense")
    category2 = TransactionCategoryFactory(user=auth_user, category_type="expense")

    BudgetCategoryFactory(budget=budget, category=category1)
    BudgetCategoryFactory(budget=budget, category=category2)

    return budget


# ============================================================================
# GOAL FIXTURES
# ============================================================================


@pytest.fixture
def goal(db, auth_user):
    """Create a test goal."""
    return GoalFactory(user=auth_user)


@pytest.fixture
def multiple_goals(db, auth_user):
    """Create multiple test goals."""
    return [
        GoalFactory(user=auth_user, goal_type="savings"),
        GoalFactory(user=auth_user, goal_type="debt"),
        GoalFactory(user=auth_user, goal_type="purchase"),
    ]


# ============================================================================
# NOTIFICATION FIXTURES
# ============================================================================


@pytest.fixture
def notification(db, auth_user):
    """Create a test notification."""
    return NotificationFactory(user=auth_user)


@pytest.fixture
def multiple_notifications(db, auth_user):
    """Create multiple test notifications."""
    return [NotificationFactory(user=auth_user) for _ in range(5)]


# ============================================================================
# API CLIENT FIXTURES
# ============================================================================


@pytest.fixture
def api_client():
    """Create a REST API client."""
    return APIClient()


@pytest.fixture
def authenticated_api_client(db, auth_user):
    """Create an authenticated REST API client."""
    client = APIClient()

    # Generate JWT tokens
    refresh = RefreshToken.for_user(auth_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    return client


@pytest.fixture
def jwt_tokens(db, auth_user):
    """Generate JWT tokens for testing."""
    refresh = RefreshToken.for_user(auth_user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


# ============================================================================
# GRAPHQL FIXTURES
# ============================================================================


@pytest.fixture
def graphql_client(db):
    """Create a GraphQL client."""
    from django.test import Client

    return Client()


@pytest.fixture
def authenticated_graphql_client(db, auth_user, jwt_tokens):
    """Create an authenticated GraphQL client."""
    from django.test import Client

    client = Client()

    # Add JWT token to headers
    client.defaults["HTTP_AUTHORIZATION"] = f'Bearer {jwt_tokens["access"]}'

    return client


# ============================================================================
# UTILITY FIXTURES
# ============================================================================


@pytest.fixture
def sample_data(db, auth_user):
    """Create a comprehensive sample dataset for testing."""
    accounts = [
        AccountFactory(user=auth_user, account_type="bank"),
        AccountFactory(user=auth_user, account_type="mobile_money"),
    ]

    categories = [
        TransactionCategoryFactory(user=auth_user, category_type="expense"),
        TransactionCategoryFactory(user=auth_user, category_type="expense"),
        TransactionCategoryFactory(user=auth_user, category_type="income"),
    ]

    transactions = [
        TransactionFactory(
            user=auth_user,
            account=accounts[0],
            category=categories[i % len(categories)],
        )
        for i in range(10)
    ]

    budget = BudgetFactory(user=auth_user)
    BudgetCategoryFactory(budget=budget, category=categories[0])
    BudgetCategoryFactory(budget=budget, category=categories[1])

    goals = [
        GoalFactory(user=auth_user),
        GoalFactory(user=auth_user),
    ]

    notifications = [
        NotificationFactory(user=auth_user),
        NotificationFactory(user=auth_user),
    ]

    return {
        "user": auth_user,
        "accounts": accounts,
        "categories": categories,
        "transactions": transactions,
        "budget": budget,
        "goals": goals,
        "notifications": notifications,
    }


# ============================================================================
# MARKS
# ============================================================================


def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "graphql: marks tests as GraphQL tests")
    config.addinivalue_line("markers", "rest: marks tests as REST API tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
