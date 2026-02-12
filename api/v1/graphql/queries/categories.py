import graphene
from django.db.models import Q

from apps.categories.models import Category
from ..types.categories import CategoryType


class CategoryQueries(graphene.ObjectType):
    category = graphene.Field(CategoryType, id=graphene.UUID())
    categories = graphene.List(
        CategoryType,
        category_type=graphene.String(),
    )

    def resolve_category(self, info, id):
        if not info.context.user.is_authenticated:
            return None
        try:
            return Category.objects.get(
                Q(pk=id),
                Q(is_system=True) | Q(user=info.context.user),
            )
        except Category.DoesNotExist:
            return None

    def resolve_categories(self, info, category_type=None):
        if not info.context.user.is_authenticated:
            return []
        queryset = Category.objects.filter(
            Q(is_system=True) | Q(user=info.context.user)
        ).filter(is_active=True)
        if category_type:
            queryset = queryset.filter(category_type=category_type)
        return queryset
