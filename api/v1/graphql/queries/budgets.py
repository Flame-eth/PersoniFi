import graphene
from apps.budgets.models import Budget
from ..types.budgets import BudgetType


class BudgetQueries(graphene.ObjectType):
    budget = graphene.Field(BudgetType, id=graphene.UUID())
    budgets = graphene.List(BudgetType, is_active=graphene.Boolean())

    def resolve_budget(self, info, id):
        if not info.context.user.is_authenticated:
            return None
        try:
            return Budget.objects.get(pk=id, user=info.context.user)
        except Budget.DoesNotExist:
            return None

    def resolve_budgets(self, info, is_active=None):
        if not info.context.user.is_authenticated:
            return []
        queryset = Budget.objects.filter(user=info.context.user)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset.order_by("-start_date")
