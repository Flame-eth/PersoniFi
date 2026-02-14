# PersoniFi - Quick Reference Guide

## 📌 Project Overview

**PersoniFi** is a personal finance SaaS platform designed for African markets, providing comprehensive expense tracking, budgeting, and financial insights through both REST and GraphQL APIs.

---

## 🎯 What Makes This Special?

### African-First Features

1. **Mobile Money Integration** (M-Pesa, Airtel Money, MTN MoMo)
2. **Multi-Currency Support** (NGN, KES, GHS, ZAR, UGX, etc.)
3. **Remittance Tracking** (Family support expenses)
4. **Data-Conscious Design** (GraphQL to reduce bandwidth)
5. **SMS Notifications** (Not just email/push)
6. **Localization** (English, French, Swahili, Hausa, Yoruba, Igbo)

### Technical Excellence

1. **Dual API Support** (REST + GraphQL for maximum flexibility)
2. **Scalable Architecture** (Domain-driven design, ready for microservices)
3. **Production-Ready** (Docker, CI/CD, monitoring from day 1)
4. **Security-First** (JWT, encryption, 2FA, audit logs)
5. **Test Coverage** (Target: 85%+)
6. **Modern Stack** (Django 5.2, PostgreSQL 15, Python 3.11+)

---

## 📁 Core Apps

| App             | Purpose                   | Key Models                          |
| --------------- | ------------------------- | ----------------------------------- |
| `users`         | Authentication & profiles | User, UserProfile, MFADevice        |
| `accounts`      | Financial accounts        | Account, Bank, MobileMoneyProvider  |
| `transactions`  | Income/expense tracking   | Transaction, RecurringTransaction   |
| `categories`    | Organize transactions     | Category                            |
| `budgets`       | Budget planning           | Budget, BudgetCategory, BudgetAlert |
| `goals`         | Financial goals           | Goal, GoalContribution              |
| `analytics`     | Reports & insights        | FinancialSnapshot, NetWorthHistory  |
| `notifications` | Multi-channel alerts      | Notification                        |
| `integrations`  | Third-party APIs          | Integration, UserIntegration        |
| `subscriptions` | SaaS billing              | Subscription, Plan, Payment         |

---

## 🔌 API Endpoints (Sample)

### REST API (`/api/v1/`)

```
Authentication:
POST   /auth/register/
POST   /auth/login/
POST   /auth/refresh/
POST   /auth/logout/

Accounts:
GET    /accounts/
POST   /accounts/
GET    /accounts/{id}/
PATCH  /accounts/{id}/
DELETE /accounts/{id}/

Transactions:
GET    /transactions/
POST   /transactions/
GET    /transactions/{id}/
PATCH  /transactions/{id}/
DELETE /transactions/{id}/
POST   /transactions/bulk-import/

Budgets:
GET    /budgets/
POST   /budgets/
GET    /budgets/{id}/
GET    /budgets/{id}/summary/

Analytics:
GET    /analytics/spending-trends/
GET    /analytics/category-breakdown/
GET    /analytics/net-worth/
```

### GraphQL (`/graphql`)

```graphql
# Query Example
query {
  me {
    email
    accounts {
      name
      balance
      currency
    }
    transactions(first: 10) {
      edges {
        node {
          amount
          description
          category {
            name
          }
        }
      }
    }
  }
}

# Mutation Example
mutation {
  createTransaction(
    input: {
      accountId: "123e4567-e89b-12d3-a456-426614174000"
      amount: 5000
      currency: "KES"
      description: "Groceries"
      categoryId: "789..."
    }
  ) {
    transaction {
      id
      amount
      description
    }
  }
}
```

---

## 🛠️ Tech Stack

### Core

- **Backend**: Django 5.2
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Task Queue**: Celery 5+

### APIs

- **REST**: Django REST Framework 3.15+
- **GraphQL**: Graphene-Django 3.0+
- **Auth**: JWT (djangorestframework-simplejwt, django-graphql-jwt)

### DevOps

- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx
- **App Server**: Gunicorn
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry, Datadog

### Integrations

- **Payments**: Paystack, Flutterwave, Stripe
- **SMS**: Africa's Talking, Twilio
- **Email**: SendGrid, Mailgun
- **Cloud**: AWS S3, DigitalOcean Spaces

---

## 🚀 Quick Start Commands

Once the project is set up, these are your primary commands:

### Development

```bash
# Start development environment
docker-compose up

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Start Celery worker
celery -A config worker -l info

# Start Celery beat (scheduled tasks)
celery -A config beat -l info
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/unit/test_transactions.py

# Run specific test
pytest tests/unit/test_transactions.py::TestTransactionModel::test_creation
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
pylint apps/

# Type checking
mypy apps/
```

### Database

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create test data
python manage.py seed_data

# Database shell
python manage.py dbshell
```

### API Documentation

```bash
# Generate OpenAPI schema
python manage.py spectacular --file schema.yml

# Access docs at:
# http://localhost:8000/api/schema/swagger-ui/  (Swagger)
# http://localhost:8000/api/schema/redoc/       (ReDoc)
# http://localhost:8000/graphql                 (GraphiQL)
```

---

## 📊 Database Schema (Simplified)

```
User (users)
├── id (UUID)
├── email (unique)
├── phone_number
├── base_currency
└── language_preference

Account (accounts)
├── id (UUID)
├── user_id (FK → User)
├── name
├── account_type (bank/mobile_money/cash/investment)
├── currency
├── balance
└── institution

Transaction (transactions)
├── id (UUID)
├── user_id (FK → User)
├── account_id (FK → Account)
├── category_id (FK → Category)
├── amount
├── currency
├── transaction_type (income/expense)
├── date
├── description
└── payment_method

Category (categories)
├── id (UUID)
├── user_id (FK → User, nullable for system categories)
├── name
├── icon
├── category_type (income/expense)
└── parent_category_id (FK → Category, for subcategories)

Budget (budgets)
├── id (UUID)
├── user_id (FK → User)
├── name
├── total_amount
├── start_date
└── end_date

BudgetCategory (budget_categories)
├── id (UUID)
├── budget_id (FK → Budget)
├── category_id (FK → Category)
├── allocated_amount
└── alert_threshold

Goal (goals)
├── id (UUID)
├── user_id (FK → User)
├── name
├── target_amount
├── current_amount
├── currency
├── deadline
└── goal_type
```

---

## 🔐 Security Checklist

- [x] JWT authentication with short-lived tokens
- [x] Password hashing (Argon2)
- [x] 2FA/MFA support
- [x] Rate limiting on API endpoints
- [x] HTTPS only in production
- [x] Sensitive data encryption (account numbers, API keys)
- [x] SQL injection prevention (Django ORM)
- [x] XSS prevention (Django templates)
- [x] CSRF protection
- [x] CORS properly configured
- [x] Secrets in environment variables (never in code)
- [x] Regular dependency updates
- [x] Security headers (HSTS, CSP, X-Frame-Options)
- [x] Audit logging
- [x] Data backup strategy

---

## 📈 Performance Targets

| Metric              | Target                    |
| ------------------- | ------------------------- |
| API Response Time   | < 200ms (95th percentile) |
| Database Query Time | < 50ms average            |
| Uptime              | 99.9%                     |
| Test Coverage       | > 85%                     |
| Page Load Time      | < 3 seconds               |
| Concurrent Users    | 10,000+                   |
| Transactions/Second | 100+                      |

---

## 🌍 Supported Countries (Initial Launch)

| Country      | Currency | Mobile Money              | Status     |
| ------------ | -------- | ------------------------- | ---------- |
| Nigeria      | NGN      | Paga, OPay                | Priority 1 |
| Kenya        | KES      | M-Pesa                    | Priority 1 |
| Ghana        | GHS      | MTN MoMo, Vodafone Cash   | Priority 2 |
| South Africa | ZAR      | -                         | Priority 2 |
| Uganda       | UGX      | MTN, Airtel Money         | Priority 3 |
| Tanzania     | TZS      | M-Pesa, Tigo Pesa, Airtel | Priority 3 |

---

## 📦 Key Dependencies

```txt
# Core
Django==5.2.11
djangorestframework==3.15.2
graphene-django==3.2.0
psycopg2-binary==2.9.9
celery==5.3.6
redis==5.0.1

# Authentication
djangorestframework-simplejwt==5.3.1
django-graphql-jwt==0.4.0
django-otp==1.5.0

# API Enhancements
drf-spectacular==0.27.2
django-filter==24.2
django-cors-headers==4.3.1
graphene-file-upload==1.3.0

# Utilities
python-decouple==3.8
django-extensions==3.2.3
django-encrypted-model-fields==0.6.5
phonenumbers==8.13.26

# Testing
pytest==8.1.1
pytest-django==4.8.0
pytest-cov==4.1.0
factory-boy==3.3.0
faker==24.0.0

# Monitoring
sentry-sdk==1.40.6
django-debug-toolbar==4.3.0

# Payments
paystack==1.6.0
flutterwave==1.2.0
stripe==8.9.0

# SMS/Email
africastalking==1.4.0
sendgrid==6.11.0
twilio==9.0.4
```

---

## 🎯 Next Steps (Once Approved)

1. **Review the development plan** → Provide feedback
2. **Confirm priorities** → Which features first?
3. **Choose deployment platform** → AWS, DigitalOcean, Azure?
4. **Setup development environment** → Docker, dependencies
5. **Begin Phase 1** → Project restructuring
6. **Implement core apps** → Users, accounts, transactions
7. **Build API layer** → REST + GraphQL
8. **Testing & deployment** → CI/CD pipeline

---

## 📞 Questions to Answer

Before we begin implementation, please clarify:

1. **Target markets**: Which African countries are priority? (Nigeria, Kenya, Ghana?)
2. **Timeline**: Is the 16-week timeline acceptable, or do you need faster/slower?
3. **Team size**: Solo developer or team?
4. **Budget**: Any constraints on paid services?
5. **Mobile money**: Which providers are most critical initially?
6. **Deployment**: Preference for cloud provider (AWS, DigitalOcean, Azure)?
7. **MVP scope**: Want to launch with all features, or start with a subset?

---

## 📚 Documentation Links

- **Development Plan**: See `DEVELOPMENT_PLAN.md` for full project roadmap
- **Architecture Decisions**: See `ARCHITECTURE_DECISIONS.md` for rationale behind key choices
- **API Documentation**: Will be auto-generated at `/api/schema/swagger-ui/`
- **Database Schema**: Will be documented in `/docs/architecture/database.md`

---

**Ready to build PersoniFi? Let's discuss the plan and get started! 🚀**
