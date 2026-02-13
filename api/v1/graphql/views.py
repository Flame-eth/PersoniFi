"""
Custom GraphQL view with authentication enforcement.

This module provides a secure GraphQL view that enforces authentication
globally, ensuring that unauthenticated users cannot access any GraphQL
endpoints.
"""

from typing import Dict, Any

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from graphene_django.views import GraphQLView as BaseGraphQLView


class SecureGraphQLView(BaseGraphQLView):
    """
    Custom GraphQL view that enforces authentication globally.

    All requests must include a valid JWT token in the Authorization header.
    Unlike the standard GraphQLView, this will reject unauthenticated requests
    with a 401 error rather than allowing them through.

    Configuration:
        In urls.py, use:
            path('graphql/', SecureGraphQLView.as_view(schema=schema), name='graphql')
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to enforce authentication before processing the request.
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            # Check if this is a query request (not schema introspection from unauthenticated users)
            if self._should_require_auth(request):
                return JsonResponse(
                    {
                        "errors": [
                            {
                                "message": "Authentication required. Please provide a valid token.",
                                "code": "UNAUTHENTICATED",
                                "extensions": {"code": "UNAUTHENTICATED"},
                            }
                        ]
                    },
                    status=401,
                )

        return super().dispatch(request, *args, **kwargs)

    def _should_require_auth(self, request) -> bool:
        """
        Determine if authentication should be required for this request.

        Note: We currently require auth for all requests. If you need to allow
        schema introspection for unauthenticated users in development, you can
        customize this method.
        """
        # For now, require authentication for all requests
        # This is the secure default approach
        return True

    @staticmethod
    def get_context(request):
        """Ensure request context is properly set for GraphQL."""
        return request


class DevelopmentGraphQLView(SecureGraphQLView):
    """
    GraphQL view for development that allows schema introspection
    without authentication, but requires auth for actual queries/mutations.

    Use this in development settings only.
    """

    def _should_require_auth(self, request) -> bool:
        """
        Allow unauthenticated schema introspection queries in development.
        """
        # Allow GET requests for GraphQL UI/docs
        if request.method == "GET":
            return False

        # Check if this is an introspection query via POST
        if request.method == "POST":
            try:
                import json

                body = json.loads(request.body)
                query = body.get("query", "").strip()
                # IntrospectionQuery is used by tools like GraphiQL
                if "__schema" in query or "IntrospectionQuery" in query:
                    return False
            except (json.JSONDecodeError, AttributeError, TypeError):
                pass

        return True
