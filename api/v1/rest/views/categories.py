from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from apps.categories.models import Category
from ..serializers.categories import CategorySerializer
from ..permissions import IsOwner


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing categories.
    Returns system categories and user's custom categories.
    """

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        # Return system categories and user's own categories
        return Category.objects.filter(
            Q(is_system=True) | Q(user=self.request.user)
        ).filter(is_active=True)

    def perform_destroy(self, instance):
        # Don't allow deleting system categories
        if instance.is_system:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Cannot delete system categories")
        # Soft delete user categories
        instance.is_active = False
        instance.save()
