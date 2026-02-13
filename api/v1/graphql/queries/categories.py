import graphene
from django.db.models import Q

from apps.categories.models import Category
from ..types.categories import CategoryType
from ..authentication import login_required


class CategoryQueries(graphene.ObjectType):
    category = graphene.Field(CategoryType, id=graphene.UUID())
    categories = graphene.List(
        CategoryType,
        category_type=graphene.String(),
    )

    @login_required
    def resolve_category(self, info, id):
        """Retrieve a category by ID (system categories or user's own)."""
        try:
            return Category.objects.get(
                Q(pk=id),
                Q(is_system=True) | Q(user=info.context.user),
            )
        except Category.DoesNotExist:
            return None

    @login_required
    def resolve_categories(self, info, category_type=None):
        """Retrieve all available categories (system + user's own)."""
        queryset = Category.objects.filter(
            Q(is_system=True) | Q(user=info.context.user)
        ).filter(is_active=True)
        if category_type:
            queryset = queryset.filter(category_type=category_type)
        return queryset
