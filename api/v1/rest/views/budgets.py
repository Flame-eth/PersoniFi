from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.budgets.models import Budget, BudgetCategory
from apps.transactions.models import Transaction
from ..serializers.budgets import BudgetSerializer, BudgetCategorySerializer
from ..permissions import IsOwner
from ..filters import BudgetFilter


class BudgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing budgets.
    """

    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = BudgetFilter
    search_fields = ["name"]
    ordering_fields = ["name", "start_date", "created_at"]
    ordering = ["-start_date"]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).prefetch_related(
            "categories__category"
        )

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        """
        Get budget summary with spending progress.
        """
        budget = self.get_object()

        # Calculate total spent within budget period
        spent = (
            Transaction.objects.filter(
                user=request.user,
                transaction_type="expense",
                date__gte=budget.start_date,
                date__lte=budget.end_date,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        return Response(
            {
                "budget_id": budget.id,
                "name": budget.name,
                "total_amount": budget.total_amount,
                "spent": spent,
                "remaining": budget.total_amount - spent,
                "percentage_used": (
                    round((spent / budget.total_amount) * 100, 2)
                    if budget.total_amount > 0
                    else 0
                ),
            }
        )


class BudgetCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing budget categories.
    """

    serializer_class = BudgetCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BudgetCategory.objects.filter(budget__user=self.request.user)
