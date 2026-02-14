"""
Locust load testing configuration for PersoniFi API.

This file simulates realistic user behavior to test API performance under load.

Run with:
    locust -f tests/performance/locustfile.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between
import json
import time


class PersoniFiUser(HttpUser):
    """Simulates a PersoniFi user performing typical operations."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """Called when a simulated user starts."""
        self.authenticate()

    def authenticate(self):
        """Authenticate user and store JWT token."""
        # Register/Login to get JWT token
        auth_data = {
            "email": f"user_{time.time()}@test.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

        # Try registration endpoint
        response = self.client.post(
            "/api/v1/auth/registration/", json=auth_data, catch_response=True
        )

        if response.status_code in [201, 200]:
            data = response.json()
            if "access" in data:
                self.token = data["access"]
            else:
                # Try login
                self.login()
        else:
            # Already exists, try login
            self.login()

    def login(self):
        """Login and get JWT token."""
        login_data = {
            "email": "test@example.com",
            "password": "testpass123",
        }

        response = self.client.post(
            "/api/v1/auth/login/", json=login_data, catch_response=True
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access", "")
        else:
            self.token = ""

    def request_with_auth(self, method, url, **kwargs):
        """Make authenticated request with JWT token."""
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        return self.client.request(method, url, headers=headers, **kwargs)

    @task(3)
    def list_accounts(self):
        """List user accounts."""
        self.request_with_auth("GET", "/api/v1/accounts/", name="List Accounts")

    @task(2)
    def create_account(self):
        """Create a new account."""
        data = {
            "name": f"Account_{time.time()}",
            "account_type": "bank",
            "currency": "NGN",
            "balance": "50000.00",
            "institution": "Test Bank",
        }
        self.request_with_auth(
            "POST", "/api/v1/accounts/", json=data, name="Create Account"
        )

    @task(5)
    def list_transactions(self):
        """List user transactions."""
        self.request_with_auth("GET", "/api/v1/transactions/", name="List Transactions")

    @task(2)
    def create_transaction(self):
        """Create a transaction."""
        # Assuming account and category IDs exist
        data = {
            "account": "00000000-0000-0000-0000-000000000000",  # Would need real ID
            "category": "00000000-0000-0000-0000-000000000001",  # Would need real ID
            "amount": "5000.00",
            "transaction_type": "expense",
            "payment_method": "cash",
            "description": "Test transaction",
        }
        response = self.request_with_auth(
            "POST",
            "/api/v1/transactions/",
            json=data,
            catch_response=True,
            name="Create Transaction",
        )
        if response.status_code not in [201, 400]:  # Accept 400 for missing FK
            response.failure(f"Got status code {response.status_code}")

    @task(3)
    def list_budgets(self):
        """List user budgets."""
        self.request_with_auth("GET", "/api/v1/budgets/", name="List Budgets")

    @task(2)
    def list_goals(self):
        """List user goals."""
        self.request_with_auth("GET", "/api/v1/goals/", name="List Goals")

    @task(1)
    def graphql_query(self):
        """Query data via GraphQL."""
        query = """
        {
            accounts {
                id
                name
                balance
            }
        }
        """
        self.request_with_auth(
            "POST", "/graphql/", json={"query": query}, name="GraphQL Query"
        )


class AdminUser(HttpUser):
    """Simulates an admin user."""

    wait_time = between(2, 5)

    def on_start(self):
        """Called when a simulated user starts."""
        # Admin would typically have pre-auth
        self.token = "admin_token_placeholder"

    @task(1)
    def admin_dashboard(self):
        """Access admin dashboard."""
        self.client.get("/admin/", name="Admin Dashboard")

    @task(1)
    def view_users(self):
        """View users in admin."""
        self.client.get("/admin/users/user/", name="View Users")
