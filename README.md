# PersoniFi - Personal Finance SaaS Backend

A production-ready Django backend for personal finance management, tailored for Nigeria with support for NGN and USD currencies.

## Features

- 🔐 **Authentication**: JWT-based auth with Google OAuth integration
- 💰 **Account Management**: Track bank accounts, mobile money, and cash
- 💸 **Transaction Tracking**: Income and expense management with categories
- 📊 **Budgets & Goals**: Budget planning and financial goal tracking
- 📈 **Analytics**: Spending trends, category breakdowns, net worth tracking
- 🔔 **Notifications**: In-app notification system
- 🌐 **Dual API**: Both REST and GraphQL APIs

## Tech Stack

- **Framework**: Django 5.2
- **APIs**: Django REST Framework + Graphene-Django
- **Database**: PostgreSQL (configurable via env)
- **Cache**: Redis (configurable via env)
- **Authentication**: JWT with SimpleJWT
- **Documentation**: OpenAPI/Swagger + GraphiQL

## Project Structure

```
PersoniFi/
├── apps/                    # Django applications
│   ├── core/               # Shared utilities and base models
│   ├── users/              # Custom user model
│   ├── accounts/           # Financial accounts
│   ├── transactions/       # Transaction tracking
│   ├── categories/         # Transaction categories
│   ├── budgets/            # Budget management
│   ├── goals/              # Financial goals
│   ├── analytics/          # Reports and insights
│   ├── notifications/      # Notification system
│   ├── integrations/       # Third-party integrations
│   └── subscriptions/      # SaaS billing
├── api/
│   └── v1/
│       ├── rest/           # REST API (DRF)
│       └── graphql/        # GraphQL API
├── config/                 # Project configuration
│   ├── settings/           # Environment-based settings
│   ├── urls.py            # Root URL config
│   ├── wsgi.py
│   └── asgi.py
└── requirements/           # Dependencies by environment
```

## Setup

### 1. Clone and Install Dependencies

```bash
cd PersoniFi
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/development.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database and Redis credentials
```

Required environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth secret

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

## API Endpoints

### REST API

Base URL: `http://localhost:8000/api/v1/`

**Authentication:**

- `POST /api/v1/auth/registration/` - Register
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout
- `GET /api/v1/users/me/` - Current user profile
- `PATCH /api/v1/users/me/` - Update profile

**Accounts:**

- `GET /api/v1/accounts/` - List accounts
- `POST /api/v1/accounts/` - Create account
- `GET /api/v1/accounts/{id}/` - Get account
- `PATCH /api/v1/accounts/{id}/` - Update account
- `DELETE /api/v1/accounts/{id}/` - Delete account

**Transactions:**

- `GET /api/v1/transactions/` - List transactions
- `POST /api/v1/transactions/` - Create transaction
- `GET /api/v1/transactions/{id}/` - Get transaction
- `PATCH /api/v1/transactions/{id}/` - Update transaction
- `DELETE /api/v1/transactions/{id}/` - Delete transaction
- `GET /api/v1/transactions/summary/` - Transaction summary
- `GET /api/v1/transactions/by_category/` - Group by category

**Budgets:**

- `GET /api/v1/budgets/` - List budgets
- `POST /api/v1/budgets/` - Create budget
- `GET /api/v1/budgets/{id}/` - Get budget
- `GET /api/v1/budgets/{id}/summary/` - Budget summary with progress

**Goals:**

- `GET /api/v1/goals/` - List goals
- `POST /api/v1/goals/` - Create goal
- `GET /api/v1/goals/{id}/` - Get goal

**Analytics:**

- `GET /api/v1/analytics/spending_trends/` - Spending trends
- `GET /api/v1/analytics/category_breakdown/` - Category breakdown
- `GET /api/v1/analytics/income_vs_expenses/` - Income vs expenses
- `GET /api/v1/analytics/net_worth/` - Net worth calculation
- `GET /api/v1/analytics/monthly_summary/` - Monthly summary

### GraphQL API

Endpoint: `http://localhost:8000/graphql/`

**Sample Query:**

```graphql
query {
  me {
    email
    firstName
    lastName
  }
  accounts {
    id
    name
    balance
    currency
  }
  transactions(transactionType: "expense") {
    id
    amount
    description
    date
    category {
      name
    }
  }
}
```

**Sample Mutation:**

```graphql
mutation {
  createTransaction(
    accountId: "your-account-id"
    amount: 5000
    currency: "NGN"
    transactionType: "expense"
    paymentMethod: "cash"
    description: "Groceries"
  ) {
    success
    transaction {
      id
      amount
      description
    }
    errors
  }
}
```

## API Documentation

- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **GraphiQL**: http://localhost:8000/graphql/

## Testing

```bash
# Install test dependencies
pip install -r requirements/testing.txt

# Run tests
pytest

# Run with coverage
pytest --cov
```

## Deployment

1. Set environment to production:

   ```bash
   export DJANGO_ENV=production
   ```

2. Install production dependencies:

   ```bash
   pip install -r requirements/production.txt
   ```

3. Collect static files:

   ```bash
   python manage.py collectstatic
   ```

4. Run with Gunicorn:
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```

## Supported Currencies

- NGN (Nigerian Naira) - Default
- USD (US Dollar)

## License

Proprietary

## Support

For issues and feature requests, please contact the development team.
