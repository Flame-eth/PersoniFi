# GraphQL Development Guidelines

## For New GraphQL Resolvers

To ensure all new GraphQL endpoints are secure, follow these patterns:

### Writing New Queries

**CORRECT ✅** - Uses `@login_required` decorator:

```python
import graphene
from ..authentication import login_required

class MyNewQuery(graphene.ObjectType):
    my_data = graphene.Field(MyDataType)

    @login_required
    def resolve_my_data(self, info):
        """Get my data - only authenticated users can access."""
        user = info.context.user
        # At this point, user is GUARANTEED to be authenticated
        return MyData.objects.filter(user=user)
```

**WRONG ❌** - Does NOT use decorator:

```python
# DO NOT DO THIS!
def resolve_my_data(self, info):
    if not info.context.user.is_authenticated:
        return None
    # This manual check is error-prone and can be forgotten
```

### Writing New Mutations

**CORRECT ✅** - Uses `@login_required` decorator with `@staticmethod`:

```python
from ..authentication import login_required

class CreateMyData(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    my_data = graphene.Field(MyDataType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    @login_required
    def mutate(mutate_self, info, name):
        """Create new data - requires authentication."""
        user = info.context.user
        # User is guaranteed to be authenticated here
        try:
            obj = MyData.objects.create(user=user, name=name)
            return CreateMyData(success=True, my_data=obj, errors=[])
        except Exception as e:
            return CreateMyData(success=False, errors=[str(e)])
```

**WRONG ❌** - Missing decorator:

```python
# DO NOT DO THIS!
def mutate(self, info, name):
    user = info.context.user
    if not user.is_authenticated:  # Easy to forget, creates vulnerability
        return CreateMyData(success=False, errors=["Auth required"])
```

### Using Permission-Based Access

For endpoints that need specific permissions:

```python
from ..authentication import permission_required

class DeleteAccount(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @staticmethod
    @permission_required('accounts.delete_account')
    def mutate(mutate_self, info, id):
        """Delete account - requires specific permission."""
        # User has both authentication AND the required permission
        account = Account.objects.get(pk=id)
        account.delete()
        return DeleteAccount(success=True)
```

### Checking Object Ownership

Use the `is_owner_or_raise` utility for ownership verification:

```python
from ..authentication import is_owner_or_raise, login_required

class UpdateMyData(graphene.Mutation):
    @staticmethod
    @login_required
    def mutate(mutate_self, info, id, **fields):
        user = info.context.user
        obj = MyData.objects.get(pk=id)

        # Verify user owns this object
        is_owner_or_raise(obj, user)  # Raises PermissionError if not owner

        # Safe to proceed
        for field, value in fields.items():
            setattr(obj, field, value)
        obj.save()
        return UpdateMyData(success=True)
```

## Testing New Resolvers

Always write tests that verify authentication is enforced:

```python
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_query_requires_authentication(client):
    """Test that unauthenticated requests are rejected."""
    query = """
    {
        myData {
            id
        }
    }
    """

    # Without authentication - should fail
    response = client.post('/graphql/', {'query': query})
    assert response.status_code == 401
    assert 'Authentication required' in str(response.content)

@pytest.mark.django_db
def test_query_with_authentication(client, django_user_model):
    """Test that authenticated requests work."""
    user = django_user_model.objects.create(email='test@test.com', password='test')
    token = get_user_token(user)  # Your token generation function

    headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    response = client.post('/graphql/', {'query': query}, **headers)
    assert response.status_code == 200
```

## Checklist Before Pushing Code

- [ ] All new GraphQL resolvers use `@login_required` decorator
- [ ] All mutations use `@staticmethod @login_required` pattern
- [ ] Object ownership is verified with `is_owner_or_raise` when needed
- [ ] Tests verify authentication is enforced
- [ ] Error messages don't leak sensitive info
- [ ] No manual `if not user.is_authenticated` checks (use decorator)
- [ ] Code review specifically checks for auth implementation

## Common Mistakes

### Mistake 1: Forgetting the Decorator

```python
# ❌ VULNERABLE!
def resolve_user_data(self, info):  # No @login_required
    return UserData.objects.filter(user=info.context.user)

# ✅ SECURE
@login_required
def resolve_user_data(self, info):
    return UserData.objects.filter(user=info.context.user)
```

### Mistake 2: Returning Empty Results Instead of Error

```python
# ❌ Not ideal - confuses clients
@login_required
def resolve_account(self, info, id):
    try:
        return Account.objects.get(pk=id, user=info.context.user)
    except Account.DoesNotExist:
        return None  # Client doesn't know if account exists or isn't authenticated

# ✅ Better - let decorator raise PermissionError
# The endpoint-level view will catch it and return proper error
```

### Mistake 3: Using `@staticmethod` Without Proper Signature

```python
# ❌ WRONG - decorator doesn't work properly
@login_required
def mutate(self, info, ...):  # Missing @staticmethod
    ...

# ✅ CORRECT - both decorators needed for mutations
@staticmethod
@login_required
def mutate(mutate_self, info, ...):
    ...
```

## Security Quick Reference

| Scenario               | Pattern                               | Example                              |
| ---------------------- | ------------------------------------- | ------------------------------------ |
| Public query           | `@login_required`                     | `resolve_public_data`                |
| Authenticated mutation | `@staticmethod @login_required`       | `mutate` in mutation class           |
| Permission-required    | `@permission_required('app.perm')`    | Admin-only operations                |
| Ownership check        | `is_owner_or_raise(obj, user)`        | Update user's own data               |
| Resource not found     | Raise `DoesNotExist` or return `None` | Already handled by `@login_required` |

## IDE Hints

Add this to your Python editor's snippets for quick templates:

```
# GraphQL Query Template
@login_required
def resolve_${1:name}(self, info, ${2:arguments}):
    """${3:description}."""
    user = info.context.user
    ${4:# implementation}

# GraphQL Mutation Template
@staticmethod
@login_required
def mutate(mutate_self, info, ${1:arguments}):
    """${2:description}."""
    user = info.context.user
    ${3:# implementation}
```

## Questions?

If you're unsure whether a resolver needs authentication, the answer is almost always **YES**. Default to secure, add exceptions only when explicitly required (like public API endpoints).

When in doubt, use `@login_required` - it's better to require auth on a public endpoint than to accidentally leave a private one open.
