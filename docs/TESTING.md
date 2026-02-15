# PersoniFi Testing & Performance Guide

## Quick Start

### Install Testing Dependencies

```bash
pip install -r requirements/testing.txt
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run Tests with Coverage Report

```bash
pytest tests/ --cov=apps --cov-report=html --cov-report=term
open htmlcov/index.html
```

## Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and fixtures
├── factories/                  # Factory Boy factories for test data
│   ├── user_factory.py
│   ├── account_factory.py
│   ├── transaction_factory.py
│   ├── budget_factory.py
│   ├── goal_factory.py
│   └── notification_factory.py
├── apps/                       # Unit tests organized by app
│   ├── users/
│   ├── accounts/
│   ├── transactions/
│   ├── budgets/
│   ├── goals/
│   ├── analytics/
│   ├── api_rest.py           # REST API endpoint tests
│   └── api_graphql.py        # GraphQL API tests
└── performance/               # Performance and load tests
    ├── benchmarks.py         # pytest-benchmark performance tests
    └── locustfile.py         # Locust load testing
```

## Running Specific Tests

### Unit Tests Only

```bash
# Test specific app
pytest tests/apps/users/ -v

# Test specific test class
pytest tests/apps/accounts/__init__.py::TestAccountModel -v

# Test specific test method
pytest tests/apps/transactions/__init__.py::TestTransactionModel::test_transaction_creation -v
```

### API Tests

```bash
# REST API tests only
pytest tests/apps/api_rest.py -v -m rest

# GraphQL tests only
pytest tests/apps/api_graphql.py -v -m graphql

# Both API tests
pytest tests/ -v -m "rest or graphql"
```

### Integration Tests

```bash
pytest tests/ -v -m integration
```

### Slow Tests

```bash
pytest tests/ -v -m slow
```

## Performance Testing

### Query Performance Benchmarks

```bash
# Run all performance benchmarks
pytest tests/performance/benchmarks.py -v --benchmark-only

# Run specific benchmark
pytest tests/performance/benchmarks.py::TestQueryPerformance::test_list_accounts_performance -v --benchmark-only

# Save benchmark results
pytest tests/performance/benchmarks.py --benchmark-save=baseline

# Compare with baseline
pytest tests/performance/benchmarks.py --benchmark-compare=baseline
```

### Load Testing

```bash
# Start development server
python manage.py runserver

# In another terminal, run Locust
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Open browser to http://localhost:8089
# Configure:
# - Number of users: 100
# - Spawn rate: 10 users/second
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Run with memory profiling
python -m memory_profiler script.py
```

## Test Fixtures

### User Fixtures

```python
def test_with_user(user):
    """Basic user fixture."""
    assert user.email is not None

def test_with_auth_user(auth_user):
    """Authenticated user with password."""
    assert auth_user.check_password('testpass123')

def test_with_user_data(auth_user_with_data):
    """User with associated test data."""
    assert auth_user_with_data.accounts.count() > 0
```

### Account Fixtures

```python
def test_with_account(account, auth_user):
    """Single account for user."""
    assert account.user == auth_user

def test_with_multiple_accounts(multiple_accounts):
    """Multiple accounts for user."""
    assert len(multiple_accounts) == 3
```

### Transaction Fixtures

```python
def test_with_transaction(transaction, auth_user):
    """Single transaction."""
    assert transaction.user == auth_user

def test_with_multiple_transactions(multiple_transactions):
    """Multiple transactions."""
    assert len(multiple_transactions) == 5
```

### API Fixtures

```python
def test_rest_api(authenticated_api_client):
    """Authenticated REST API client."""
    response = authenticated_api_client.get('/api/v1/accounts/')
    assert response.status_code == 200

def test_graphql_api(authenticated_graphql_client):
    """Authenticated GraphQL client."""
    response = authenticated_graphql_client.post('/graphql/', {...})
    assert response.status_code == 200
```

## Coverage Report

### Generate Coverage Report

```bash
pytest tests/ --cov=apps --cov-report=html --cov-report=term --cov-fail-under=80
```

### View Coverage by Module

```bash
pytest tests/ --cov=apps --cov-report=term-missing
```

### Coverage Targets

- **Global target**: 80% minimum
- **apps/users**: 90%+
- **apps/accounts**: 85%+
- **apps/transactions**: 85%+
- **apps/budgets**: 80%+
- **apps/goals**: 80%+
- **api/**: 75%+

## Continuous Integration

### GitHub Actions

Tests run automatically on:

- Push to main or develop
- Pull requests

### Local Pre-commit

```bash
# Install pre-commit
pip install pre-commit

# Configure hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Best Practices

### Writing Tests

```python
# Good test naming
def test_user_can_create_account(auth_user):
    """User can create an account."""
    account = AccountFactory(user=auth_user)
    assert account.user == auth_user

# Avoid vague names
def test_account():  # Bad
    pass

# Use fixtures appropriately
def test_transaction_filter(multiple_transactions, category):
    """Filter transactions by category."""
    filtered = Transaction.objects.filter(category=category)
    assert filtered.count() > 0

# Test edge cases
def test_zero_balance():
    """Account can have zero balance."""
    account = AccountFactory(balance=Decimal('0'))
    assert account.balance == Decimal('0')

def test_large_amount():
    """Transaction supports large amounts."""
    transaction = TransactionFactory(amount=Decimal('999999999.99'))
    assert transaction.amount == Decimal('999999999.99')
```

### Test Organization

```python
# Group related tests in classes
@pytest.mark.django_db
class TestAccountModel:
    def test_creation(self):
        pass

    def test_str_representation(self):
        pass

@pytest.mark.django_db
class TestAccountQuerySet:
    def test_filter(self):
        pass
```

### Database Isolation

```python
# Use pytest.mark.django_db for database access
@pytest.mark.django_db
def test_database_operations():
    pass

# Use in-memory database for fast tests
# Configured in conftest.py
```

## Debugging Tests

### Verbose Output

```bash
pytest tests/ -v -s
```

### Drop into Debugger

```python
import pytest
pytest.set_trace()  # Equivalent to pdb.set_trace()
```

### View Test Variables

```bash
pytest tests/ -v --tb=short
```

## Performance Expectations

### Query Performance

- Simple queries: < 1ms
- Filtered queries: < 5ms
- Aggregation queries: < 10ms

### API Response Time

- Account list: < 100ms
- Transaction create: < 200ms
- Analytics query: < 300ms
- GraphQL query: < 200ms

### Benchmark Thresholds

Results are compared against baseline:

```bash
# Baseline must be typically:
# - Account list: 50-100ms
# - Transaction filter: 100-200ms
# - Bulk create: 500-1000ms
```

## Troubleshooting Tests

### Database Errors

```bash
# Reset test database
pytest --create-db

# Use cleaner database
pytest --nomigrations
```

### Import Errors

```bash
# Check PYTHONPATH
export PYTHONPATH=/path/to/project:$PYTHONPATH

# Run from project root
cd /path/to/PersoniFi
pytest tests/
```

### Timeout Issues

```bash
# Increase timeout for slow tests
pytest tests/ --timeout=300
```

## Test Reporting

### HTML Report

```bash
pytest tests/ --html=report.html --self-contained-html
```

### JUnit Report

```bash
pytest tests/ --junit-xml=report.xml
```

### Coverage Badge

```bash
coverage-badge -o coverage.svg -f
```

## Next Steps

1. Run all tests: `pytest tests/ -v`
2. Check coverage: `pytest tests/ --cov=apps --cov-report=html`
3. Run benchmarks: `pytest tests/performance/ --benchmark-only`
4. Load test: `locust -f tests/performance/locustfile.py`
