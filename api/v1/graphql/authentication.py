"""
GraphQL authentication and permission utilities.

This module provides decorators and utilities for enforcing authentication
and authorization in GraphQL resolvers, ensuring consistent security across
all GraphQL endpoints.
"""

from functools import wraps
from typing import Callable, Any

import graphene
from django.contrib.auth.models import AnonymousUser


class GraphQLAuthenticationError(graphene.ObjectType):
    """Authentication error response."""

    message = graphene.String()
    code = graphene.String()


def login_required(func: Callable) -> Callable:
    """
    Decorator for GraphQL resolvers that require authentication.

    Usage:
        @login_required
        def resolve_user_data(self, info, **kwargs):
            user = info.context.user
            # User is guaranteed to be authenticated here
            ...

    Raises:
        PermissionError if user is not authenticated.
    """

    @wraps(func)
    def wrapper(self, info, *args, **kwargs):
        user = info.context.user
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            raise PermissionError(
                "Authentication required. Please provide a valid token."
            )
        return func(self, info, *args, **kwargs)

    return wrapper


def permission_required(permission: str) -> Callable:
    """
    Decorator for GraphQL resolvers that require specific permissions.

    Usage:
        @permission_required('accounts.change_account')
        def resolve_update_account(self, info, **kwargs):
            # User has the required permission
            ...

    Args:
        permission: Permission codename (e.g., 'accounts.change_account')

    Raises:
        PermissionError if user doesn't have the permission.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, info, *args, **kwargs):
            user = info.context.user
            if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
                raise PermissionError(
                    "Authentication required. Please provide a valid token."
                )

            if not user.has_perm(permission):
                raise PermissionError(f"Permission denied. Required: {permission}")

            return func(self, info, *args, **kwargs)

        return wrapper

    return decorator


def is_owner_or_raise(obj: Any, user) -> None:
    """
    Verify that the user owns the object or raise PermissionError.

    Usage:
        def resolve_account(self, info, id):
            account = Account.objects.get(pk=id)
            is_owner_or_raise(account, info.context.user)
            return account

    Args:
        obj: Model instance with a 'user' field
        user: Django user object

    Raises:
        PermissionError if user doesn't own the object.
    """
    if not hasattr(obj, "user"):
        raise ValueError("Object must have a 'user' field")

    if obj.user != user:
        raise PermissionError("Object not found or access denied.")


class AuthenticatedSchema:
    """
    Mixin for GraphQL ObjectType that provides automatic authentication.
    This can be used as a base for Query, Mutation, or other ObjectTypes
    to ensure all resolvers in that type require authentication.
    """

    @staticmethod
    def ensure_authenticated(info) -> Any:
        """Verify user is authenticated and return user object."""
        user = info.context.user
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            raise PermissionError(
                "Authentication required. Please provide a valid token."
            )
        return user
