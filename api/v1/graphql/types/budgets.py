import graphene
from graphene_django import DjangoObjectType

from apps.budgets.models import Budget, BudgetCategory


class BudgetCategoryType(DjangoObjectType):
    class Meta:
        model = BudgetCategory
        fields = (
            "id",
            "category",
            "allocated_amount",
            "alert_threshold",
            "created_at",
            "updated_at",
        )


class BudgetType(DjangoObjectType):
    class Meta:
        model = Budget
        fields = (
            "id",
            "name",
            "total_amount",
            "currency",
            "start_date",
            "end_date",
            "is_active",
            "created_at",
            "updated_at",
        )
