# PersoniFi - Key Architectural Decisions & Rationale

## 🎯 Core Design Principles

### 1. **Both REST and GraphQL APIs**

**Decision**: Implement both API paradigms in parallel.

**Why?**

- **REST for simplicity**: Third-party integrations, webhooks, and simpler clients prefer REST
- **GraphQL for flexibility**: Mobile apps can request exactly what they need, reducing bandwidth (critical for African markets with expensive data)
- **Different use cases**:
  - REST: CRUD operations, webhooks, batch jobs
  - GraphQL: Complex queries, real-time updates, mobile apps
- **Industry trend**: Leading FinTech apps (Stripe, PayPal) support both

**Trade-offs**:

- ❌ More maintenance overhead
- ❌ Duplicate logic (mitigated by shared serialization layer)
- ✅ Maximum client flexibility
- ✅ Future-proof architecture

---

### 2. **Django Apps by Domain (Not by Function)**

**Decision**: Structure apps by business domains (`transactions`, `budgets`) rather than technical layers (`models`, `views`).

**Why?**

- ✅ **Clear boundaries**: Each app is a self-contained module
- ✅ **Team scalability**: Different teams can own different apps
- ✅ **Microservices-ready**: Easy to extract `budgets` into a separate service later
- ✅ **Testing isolation**: Test budgets independently of transactions
- ✅ **Code discovery**: New developers know exactly where to find budget logic

**Example**:

```
❌ BAD (Technical structure):
apps/
  models/
    transaction.py
    budget.py
  views/
    transaction_views.py
    budget_views.py
  serializers/
    transaction_serializers.py
    budget_serializers.py

✅ GOOD (Domain structure):
apps/
  transactions/
    models.py
    views.py
    serializers.py
    tests.py
  budgets/
    models.py
    views.py
    serializers.py
    tests.py
```

---

### 3. **Environment-Based Settings Split**

**Decision**: Split `settings.py` into `base.py`, `development.py`, `production.py`, `testing.py`.

**Why?**

- ✅ **Security**: Secrets never in version control
- ✅ **Clarity**: Production settings don't clutter development environment
- ✅ **Testing**: Test database doesn't interfere with development
- ✅ **Team coordination**: Everyone uses the same development settings

**Pattern**:

```python
# config/settings/base.py - shared settings
# config/settings/development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# config/settings/production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOST')]
```

**Usage**:

```bash
# Development
python manage.py runserver --settings=config.settings.development

# Production
export DJANGO_SETTINGS_MODULE=config.settings.production
gunicorn config.wsgi:application
```

---

### 4. **PostgreSQL Over MySQL/SQLite**

**Decision**: Use PostgreSQL as the primary database.

**Why?**

- ✅ **JSONB fields**: Store flexible metadata without schema changes
  ```python
  class Transaction(models.Model):
      metadata = models.JSONField(default=dict)
      # Store: {"merchant_lat": 1.23, "merchant_lng": 36.8, "notes": "..."}
  ```
- ✅ **Array fields**: Store tags without a join table
  ```python
  tags = ArrayField(models.CharField(max_length=50))
  ```
- ✅ **Full-text search**: Built-in search without Elasticsearch (initially)
- ✅ **Currency type**: Native `NUMERIC` with exact precision (no floating-point errors)
- ✅ **Time-series data**: Excellent for financial time-series
- ✅ **Row-level security**: Multi-tenancy support (if needed)

**Alternatives considered**:

- ❌ SQLite: Not production-ready, lacks concurrency
- ❌ MySQL: Weaker JSON support, less features

---

### 5. **JWT Authentication (Not Session-Based)**

**Decision**: Use JSON Web Tokens (JWT) for authentication.

**Why?**

- ✅ **Stateless**: Scales horizontally (no session store needed)
- ✅ **Mobile-friendly**: Tokens stored in mobile apps easily
- ✅ **API-first**: Standard for REST/GraphQL APIs
- ✅ **Microservices-ready**: Services can verify tokens independently
- ✅ **Cross-domain**: Works across subdomains (api.personifi.com, app.personifi.com)

**Security measures**:

- Short-lived access tokens (15 min)
- Long-lived refresh tokens (7 days, rotated)
- Token blacklist on logout
- Secure token storage in HTTP-only cookies (web) or Keychain (mobile)

**Implementation**:

```python
# DRF
from rest_framework_simplejwt.authentication import JWTAuthentication

# GraphQL
import graphql_jwt
```

---

### 6. **UUID Primary Keys (Not Auto-Increment IDs)**

**Decision**: Use UUIDs instead of sequential integers for primary keys.

**Why?**

- ✅ **Security**: Can't guess other users' transaction IDs
  - ❌ `/api/transactions/123/` → Try 122, 124... (enumeration attack)
  - ✅ `/api/transactions/a3f2e1c4-.../` → Unguessable
- ✅ **Distributed systems**: Unique across databases (for sharding later)
- ✅ **Merging data**: No ID conflicts when merging databases
- ✅ **Public URLs**: Safe to expose in URLs

**Trade-offs**:

- ❌ Larger storage (16 bytes vs 4 bytes)
- ❌ Slightly slower indexing
- ✅ Worth it for security in financial apps

**Implementation**:

```python
import uuid
from django.db import models

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
```

---

### 7. **Celery for Async Tasks**

**Decision**: Use Celery with Redis as the message broker.

**Why?**

- ✅ **Background jobs**: Don't block API responses
  - Send email → async
  - Sync bank account → async (can take 30 seconds)
  - Generate PDF report → async
- ✅ **Scheduled tasks**: Daily currency rate updates, recurring transactions
- ✅ **Reliability**: Task retries on failure
- ✅ **Scalability**: Add more workers as needed

**Use cases**:

```python
# Send welcome email asynchronously
@shared_task
def send_welcome_email(user_id):
    user = User.objects.get(id=user_id)
    send_mail(subject='Welcome to PersoniFi', ...)

# In view
def register_user(request):
    user = User.objects.create(...)
    send_welcome_email.delay(user.id)  # Non-blocking
    return Response({'status': 'created'})
```

---

### 8. **Redis for Caching & Real-Time Features**

**Decision**: Use Redis as the cache backend and Celery broker.

**Why?**

- ✅ **Speed**: In-memory, microsecond latency
- ✅ **Multiple use cases**:
  - API rate limiting (throttle by user)
  - Session storage (optional)
  - Celery task queue
  - Real-time data (WebSocket channels)
  - Cache expensive queries (net worth calculation)
- ✅ **Cost-effective**: Single service for multiple purposes

**Caching strategy**:

```python
from django.core.cache import cache

def get_net_worth(user_id):
    cache_key = f'net_worth:{user_id}'
    net_worth = cache.get(cache_key)

    if not net_worth:
        # Expensive calculation
        net_worth = calculate_net_worth(user_id)
        cache.set(cache_key, net_worth, timeout=300)  # 5 min

    return net_worth
```

---

### 9. **API Versioning from Day 1**

**Decision**: Version APIs via URL path (`/api/v1/`, `/api/v2/`).

**Why?**

- ✅ **Breaking changes**: Can improve API without breaking clients
- ✅ **Mobile apps**: Can't force users to update immediately
- ✅ **Backward compatibility**: Maintain v1 while v2 is adopted
- ✅ **Clear deprecation path**: Announce "v1 sunset: Dec 2027"

**Alternatives considered**:

- ❌ Header-based versioning: Less discoverable
- ❌ Query parameter: Ugly, inconsistent
- ✅ URL-based: Clear, standard, RESTful

---

### 10. **Soft Deletes Over Hard Deletes**

**Decision**: Don't actually delete records; mark as deleted with `deleted_at` timestamp.

**Why?**

- ✅ **Data recovery**: Users can undo accidental deletions
- ✅ **Audit trail**: Know who deleted what and when
- ✅ **Regulatory compliance**: Some laws require data retention
- ✅ **Analytics**: Include deleted data in historical reports

**Implementation**:

```python
class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super().delete()

# Default queryset excludes deleted
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
```

---

### 11. **Encryption for Sensitive Data**

**Decision**: Encrypt sensitive fields (account numbers, API keys) at the application level.

**Why?**

- ✅ **Defense in depth**: Even if database is compromised, data is encrypted
- ✅ **Compliance**: Required by PCI DSS, GDPR
- ✅ **Granular control**: Encrypt specific fields, not entire database

**Implementation**:

```python
from encrypted_model_fields.fields import EncryptedCharField

class Account(models.Model):
    name = models.CharField(max_length=100)
    account_number = EncryptedCharField(max_length=100)  # Encrypted
    balance = models.DecimalField(max_digits=15, decimal_places=2)
```

**Encryption key management**:

- Store key in environment variable
- Use AWS KMS or HashiCorp Vault in production
- Rotate keys periodically

---

### 12. **Multi-Currency as First-Class Feature**

**Decision**: Every amount field has an associated currency field.

**Why?**

- ✅ **African reality**: Users deal with multiple currencies daily
  - Salary in KES
  - Shopping in USD
  - Rent in local currency
- ✅ **Accurate reporting**: No assumptions about currency
- ✅ **Exchange rate tracking**: Historical rates for accurate reporting

**Implementation**:

```python
class Transaction(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    amount_in_base_currency = models.DecimalField(max_digits=15, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.currency != self.user.base_currency:
            self.exchange_rate = get_exchange_rate(self.currency, self.user.base_currency)
            self.amount_in_base_currency = self.amount * self.exchange_rate
        else:
            self.amount_in_base_currency = self.amount
        super().save(*args, **kwargs)
```

---

### 13. **Test-Driven Development (TDD)**

**Decision**: Write tests before/alongside code, aim for 85%+ coverage.

**Why?**

- ✅ **Confidence**: Know that changes don't break existing features
- ✅ **Documentation**: Tests show how code should be used
- ✅ **Refactoring safety**: Can improve code without fear
- ✅ **Faster debugging**: Tests catch bugs early
- ✅ **Financial app**: Critical to avoid money-related bugs

**Test pyramid**:

```
        E2E (10%)
       /         \
  Integration (20%)
   /              \
  Unit Tests (70%)
```

**Example**:

```python
# Test that budget alerts trigger correctly
@pytest.mark.django_db
def test_budget_alert_triggered():
    budget = BudgetFactory(amount=1000, alert_threshold=0.8)

    # Spend 850 (85%)
    TransactionFactory(
        user=budget.user,
        category=budget.category,
        amount=850
    )

    # Assert alert was created
    assert BudgetAlert.objects.filter(
        budget=budget,
        alert_type='threshold_exceeded'
    ).exists()
```

---

### 14. **Docker for Development & Production Parity**

**Decision**: Use Docker Compose for local development, matching production environment.

**Why?**

- ✅ **Consistency**: "Works on my machine" is eliminated
- ✅ **Onboarding**: New developers run `docker-compose up` and start coding
- ✅ **Services**: PostgreSQL, Redis, Celery all configured correctly
- ✅ **Production parity**: Dev environment mirrors production

**Developer experience**:

```bash
# New developer joins team
git clone github.com/yourorg/personifi
cd personifi
cp .env.example .env
docker-compose up

# Application running at http://localhost:8000
```

---

### 15. **African Market Priorities**

**Decision**: Focus on mobile money and pan-African features from day 1.

**Why?**

- ✅ **Mobile money dominance**: More Africans use M-Pesa than banks
- ✅ **Multi-currency reality**: Cross-border trade is common
- ✅ **Remittances**: Family support is a major expense category
- ✅ **Data costs**: GraphQL reduces over-fetching (saves user money)
- ✅ **Feature phones**: SMS notifications critical (not just push/email)
- ✅ **Offline-first**: Plan for intermittent connectivity (future mobile app)

**Specific adaptations**:

```python
# Transaction categories include African-specific items
AFRICAN_CATEGORIES = [
    'Airtime & Data',
    'Mobile Money Fees',
    'Remittances (Sending)',
    'Remittances (Receiving)',
    'Matatu/Bodaboda (Transport)',
    'Charcoal/Gas (Cooking Fuel)',
    'Generator Fuel',
    'Water Purchase',
]

# Payment methods
PAYMENT_METHODS = [
    ('mobile_money', 'Mobile Money (M-Pesa, etc.)'),
    ('cash', 'Cash'),
    ('bank_transfer', 'Bank Transfer'),
    ('card', 'Debit/Credit Card'),
    ('crypto', 'Cryptocurrency'),
]
```

---

## 🚀 Scalability Decisions

### Horizontal Scaling Strategy

1. **Stateless application**: JWT auth, no server-side sessions
2. **Database pooling**: PgBouncer for connection management
3. **Read replicas**: Separate read/write databases for analytics
4. **Caching layer**: Redis for frequently accessed data
5. **CDN**: Static assets served from CloudFlare
6. **Async tasks**: Offload heavy work to Celery workers
7. **API rate limiting**: Prevent abuse, manage load

### When to Optimize

**Don't**:

- Premature optimization (build it first)
- Microservices on day 1 (monolith is fine initially)

**Do**:

- Index database queries from the start
- Use `select_related()` and `prefetch_related()`
- Cache expensive operations
- Monitor performance (Sentry, Datadog)
- Load test before launch

---

## 📊 Decision Matrix

| Decision            | Complexity | Scalability | Maintainability | Cost   |
| ------------------- | ---------- | ----------- | --------------- | ------ |
| Both REST + GraphQL | High       | High        | Medium          | Low    |
| Domain-driven apps  | Medium     | High        | High            | Low    |
| PostgreSQL          | Low        | High        | High            | Medium |
| JWT Auth            | Medium     | High        | Medium          | Low    |
| Celery + Redis      | Medium     | High        | Medium          | Medium |
| Docker              | Medium     | High        | High            | Low    |
| Multi-currency      | High       | Medium      | Medium          | Low    |
| UUID PKs            | Low        | High        | High            | Low    |
| Test Coverage 85%   | High       | N/A         | High            | Medium |

---

## ⚠️ Known Trade-offs & Future Considerations

### Short-term Sacrifices

1. **No AI/ML initially**: Manual categorization first, ML in Phase 2
2. **Shared schema**: Not multi-tenant architecture yet (can add later)
3. **Monolith first**: Not microservices (split if needed at scale)
4. **PostgreSQL full-text**: Elasticsearch only if search becomes critical

### Future Enhancements

1. **Mobile apps**: React Native or Flutter (separate project)
2. **Real-time sync**: WebSocket for live updates
3. **Machine learning**: Auto-categorization, fraud detection
4. **Blockchain**: Crypto wallet tracking
5. **Open Banking**: Direct bank integrations (as APIs become available)
6. **Voice interface**: Alexa/Google Assistant for transaction entry
7. **WhatsApp bot**: Add transactions via WhatsApp messages

---

## 🎓 Learning Resources

If you're unfamiliar with any of these technologies, here are quick-start resources:

- **Django REST Framework**: https://www.django-rest-framework.org/tutorial/quickstart/
- **GraphQL/Graphene**: https://docs.graphene-python.org/projects/django/en/latest/tutorial-plain/
- **Celery**: https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html
- **Docker**: https://docs.docker.com/get-started/
- **JWT**: https://jwt.io/introduction
- **PostgreSQL**: https://www.postgresql.org/docs/current/tutorial.html

---

**This architecture is designed to:**

- ✅ Start simple, scale when needed
- ✅ Support African market specifics
- ✅ Maintain industry best practices
- ✅ Enable rapid feature development
- ✅ Ensure data security & compliance
- ✅ Provide excellent developer experience

**Questions? Let's discuss any decisions you'd like to reconsider or modify!**
