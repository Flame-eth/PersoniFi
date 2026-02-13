import graphene
from apps.budgets.models import Budget
from ..types.budgets import BudgetType
from ..authentication import login_required


class BudgetQueries(graphene.ObjectType):
    budget = graphene.Field(BudgetType, id=graphene.UUID())
    budgets = graphene.List(BudgetType, is_active=graphene.Boolean())

    @login_required
    def resolve_budget(self, info, id):
        """Retrieve a specific budget by ID (user must own it)."""
        try:
            return Budget.objects.get(pk=id, user=info.context.user)
        except Budget.DoesNotExist:
            return None

    @login_required
    def resolve_budgets(self, info, is_active=None):
        """Retrieve all budgets for the authenticated user."""
        queryset = Budget.objects.filter(user=info.context.user)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset.order_by("-start_date")
