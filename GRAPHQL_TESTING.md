# GraphQL Security - Testing Guide

This guide shows you how to test the newly implemented GraphQL authentication security layer.

## Quick Test Commands

### 1. Get an API Token

First, register or login to get a JWT token:

```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/registration/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password1": "securepassword123",
    "password2": "securepassword123"
  }'

# Or login to get token
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'

# Response will include tokens like:
# {
#   "key": "YOUR_JWT_TOKEN_HERE",
#   "access": "REFRESH_TOKEN"
# }
```

### 2. Test Unauthenticated Request (Should FAIL - 401)

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ goals { id name } }"}'

# Expected Response:
# {
#   "errors": [{
#     "message": "Authentication required. Please provide a valid token.",
#     "code": "UNAUTHENTICATED",
#     "extensions": {"code": "UNAUTHENTICATED"}
#   }]
# }
```

### 3. Test Authenticated Request (Should SUCCEED - 200)

```bash
# Replace YOUR_JWT_TOKEN with the token from step 1
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"query": "{ goals { id name targetAmount } }"}'

# Expected Response:
# {
#   "data": {
#     "goals": [] or [list of goals]
#   }
# }
```

### 4. Test Invalid Token (Should FAIL - 401)

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid_token_here" \
  -d '{"query": "{ goals { id } }"}'

# Expected Response:
# Either 401 Unauthorized or GraphQL error about invalid token
```

### 5. Test Mutation Without Auth (Should FAIL - 401)

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { createAccount(name: \"Test\", accountType: \"SAVINGS\", currency: \"NGN\") { success errors } }"
  }'

# Expected Response:
# 401 Unauthorized (at endpoint level, blocking before resolver)
```

### 6. Test Mutation With Auth (Should SUCCEED)

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "query": "mutation { createAccount(name: \"Test\", accountType: \"SAVINGS\", currency: \"NGN\") { success account { id name } errors } }"
  }'

# Expected Response:
# {
#   "data": {
#     "createAccount": {
#       "success": true,
#       "account": {"id": "uuid", "name": "Test"},
#       "errors": []
#     }
#   }
# }
```

## Using GraphiQL (Development Only)

In development mode (`DEBUG=true`), you can use GraphiQL at http://localhost:8000/graphql/

1. Open http://localhost:8000/graphql/ in your browser
2. Click on "HTTP HEADERS" (bottom left)
3. Add your authentication header:

```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

4. Now any queries/mutations will be authenticated

## Testing with Python

If you want to test programmatically:

```python
import requests
import json

# 1. Get token
auth_response = requests.post(
    "http://localhost:8000/api/v1/auth/login/",
    json={"email": "test@example.com", "password": "securepassword123"}
)
token = auth_response.json()["key"]

# 2. Make authenticated GraphQL request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

query = """
{
  goals {
    id
    name
    targetAmount
  }
}
"""

response = requests.post(
    "http://localhost:8000/graphql/",
    json={"query": query},
    headers=headers
)

print(response.json())

# 3. Test unauthenticated request
response_unauth = requests.post(
    "http://localhost:8000/graphql/",
    json={"query": query},
)

# Should return 401 or errors
print(response_unauth.json())
```

## What's Protected

All GraphQL endpoints now require authentication:

- ✅ `query { goals { ... } }`
- ✅ `query { accounts { ... } }`
- ✅ `query { transactions { ... } }`
- ✅ `query { budgets { ... } }`
- ✅ `query { categories { ... } }`
- ✅ `query { notifications { ... } }`
- ✅ `mutation { createAccount(...) { ... } }`
- ✅ `mutation { updateTransaction(...) { ... } }`
- ✅ All other mutations

### Exception: Schema Introspection (Development Only)

In development mode (`DEBUG=true`), GraphiQL can introspect the schema without authentication. This is intentional to allow development tools to work. In production, even introspection requires authentication.

## Troubleshooting

### "Invalid token" error

- Make sure you're using a valid, non-expired token
- Token format should be: `Authorization: Bearer YOUR_TOKEN_HERE`
- Not: `Authorization: Token YOUR_TOKEN_HERE` (that's for DRF)

### 401 in GraphiQL but works in curl

- Make sure you've added the Authorization header in GraphiQL's HTTP Headers section
- Refresh the page after adding headers

### Still seeing old behavior

- Clear your browser cache
- Make sure Django server has restarted and is running the latest code
- Check `config/urls.py` to ensure it's using `SecureGraphQLView`

## Security Layers Explained

1. **Endpoint Level** (`SecureGraphQLView`): Rejects unauthenticated requests with 401
2. **Resolver Level** (`@login_required`): Catches any edge cases, provides defense-in-depth

If someone manages to bypass one layer, the other protects your data.
