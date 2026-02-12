import graphene
from graphene_django import DjangoObjectType

from apps.categories.models import Category


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "category_type",
            "parent",
            "is_system",
            "is_active",
            "created_at",
            "updated_at",
        )
