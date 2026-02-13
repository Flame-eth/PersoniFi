# GraphQL Security Implementation Guide

## Problem Summary

The PersoniFi project had a critical security vulnerability:

- **REST API**: ✅ Properly secured with `IsAuthenticated` permission class and JWT authentication
- **GraphQL**: ❌ Lacked global authentication enforcement
  - Endpoint had `@csrf_exempt` but no permission classes
  - JWT middleware provided context but didn't **enforce** auth
  - Only individual resolver-level manual checks prevented unauthorized access
  - Risk: Developers could forget auth checks, exposing endpoints publicly
  - Risk: Anonymous users could still execute queries (getting empty results instead of errors)

## Solution Architecture

### Layer 1: Endpoint-Level Authentication (Strongest)

**File**: `api/v1/graphql/views.py`

**Custom `SecureGraphQLView` class** enforces authentication on the entire GraphQL endpoint:

- All requests must be authenticated (by default)
- Unauthenticated requests receive 401 error with proper error message
- Development mode (`DevelopmentGraphQLView`) allows schema introspection without auth while protecting data access

**Updated Configuration** in `config/urls.py`:

- Uses `SecureGraphQLView` in production
- Uses `DevelopmentGraphQLView` in development (for GraphiQL)

### Layer 2: Resolver-Level Authentication (Defense in Depth)

**File**: `api/v1/graphql/authentication.py`

**Decorator-based approach** for individual GraphQL resolvers:

```python
@login_required
def resolve_account(self, info, id):
    # User is guaranteed to be authenticated here
    return Account.objects.get(pk=id, user=info.context.user)
```

**Available Decorators**:

1. **`@login_required`** - Requires user authentication
2. **`@permission_required('app.permission_name')`** - Requires specific permission
3. **`is_owner_or_raise(obj, user)`** - Utility function for ownership checks

### Why Both Layers?

| Layer          | Purpose                                        | Benefit                                  |
| -------------- | ---------------------------------------------- | ---------------------------------------- |
| Endpoint-level | Blocks unauthenticated requests at entry point | Fast rejection, no query execution       |
| Resolver-level | Prevents data leakage in complex queries       | Catches edge cases, developer safety net |

This is **defense-in-depth** - if one layer is misconfigured, the other provides protection.

## Implementation Pattern

### Before (Vulnerable):

```python
def resolve_goal(self, info, id):
    if not info.context.user.is_authenticated:
        return None  # Silent failure - unclear to client
    return Goal.objects.get(pk=id, user=info.context.user)
```

### After (Secure):

```python
from api.v1.graphql.authentication import login_required

@login_required
def resolve_goal(self, info, id):
    # Guaranteed: info.context.user is authenticated
    # Unauthenticated users get 401 error at endpoint level
    return Goal.objects.get(pk=id, user=info.context.user)
```

## Changes Made

### 1. New File: `api/v1/graphql/authentication.py`

- `@login_required` decorator
- `@permission_required(perm)` decorator
- `is_owner_or_raise(obj, user)` utility
- `AuthenticatedSchema` mixin for future use

### 2. New File: `api/v1/graphql/views.py`

- `SecureGraphQLView` - Always requires authentication
- `DevelopmentGraphQLView` - Production-safe dev mode

### 3. Updated File: `config/urls.py`

- Replaced `GraphQLView` with `SecureGraphQLView` / `DevelopmentGraphQLView`
- Automatic selection based on `DEBUG` setting

### 4. Updated File: `api/v1/graphql/queries/goals.py`

- Example of updated resolver using `@login_required` decorator
- Cleaner code, explicit authentication requirement

## Migration Steps for Other Resolvers

For all remaining GraphQL queries and mutations, apply this pattern:

```python
# BEFORE
def resolve_something(self, info, **kwargs):
    if not info.context.user.is_authenticated:
        return None/[]
    # ... rest of logic

# AFTER
@login_required
def resolve_something(self, info, **kwargs):
    # ... same logic, auth is guaranteed
```

## Testing Security

### Test 1: Unauthenticated request should fail

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ goals { id } }"}'
# Expected: 401 Unauthorized with clear error message
```

### Test 2: Authenticated request should succeed

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "{ goals { id } }"}'
# Expected: 200 OK with data or empty results
```

### Test 3: Invalid token should fail

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid_token" \
  -d '{"query": "{ goals { id } }"}'
# Expected: 401 Unauthorized
```

## Key Improvements

| Aspect               | Before                | After                               |
| -------------------- | --------------------- | ----------------------------------- |
| **Auth Enforcement** | Manual per-resolver   | Global + per-resolver               |
| **Error Response**   | Silent (empty data)   | Explicit 401/403 with message       |
| **Developer Safety** | Easy to forget checks | Decorator enforces pattern          |
| **Token Validation** | Per-resolver          | At endpoint entry                   |
| **Production-Safe**  | No differentiation    | DevelopmentGraphQLView for dev mode |
| **Consistency**      | Varies by resolver    | Standardized across all endpoints   |

## Security Checklist

- [x] GraphQL endpoint requires authentication globally
- [x] JWT middleware provides token context
- [x] Custom decorators enforce auth per-resolver
- [x] Clear error messages for unauthenticated requests
- [x] Production mode blocks all unauthenticated GraphQL access
- [x] Development mode allows schema introspection only
- [x] Ownership checks prevent cross-user data access
- [x] REST API and GraphQL have equivalent security levels

## Future Enhancements

1. **Rate Limiting**: Add rate limiting decorator for GraphQL resolvers
2. **Query Complexity**: Implement query complexity analysis to prevent DOS
3. **Audit Logging**: Log all GraphQL mutations for compliance
4. **API Key Support**: Add API key authentication as alternative to JWT
5. **Automated Decorator Application**: Use parent class to auto-require auth for all resolvers

## References

- [Graphene Django Authentication](https://docs.graphene-python.org/projects/django/en/latest/tutorial-plain/)
- [OWASP: Authorization Bypass](https://owasp.org/www-community/Privilege_Escalation/Authorization_Bypass/authorization-bypass)
- [Django REST Framework Permissions](https://www.django-rest-framework.org/api-guide/permissions/)
