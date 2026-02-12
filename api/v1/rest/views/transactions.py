from django.db.models import Sum, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.transactions.models import Transaction
from ..serializers.transactions import TransactionSerializer
from ..permissions import IsOwner
from ..filters import TransactionFilter


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing transactions.
    """

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = TransactionFilter
    search_fields = ["description", "notes"]
    ordering_fields = ["date", "amount", "created_at"]
    ordering = ["-date", "-created_at"]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related(
            "account", "category"
        )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        Get transaction summary (total income, total expenses, net).
        """
        queryset = self.filter_queryset(self.get_queryset())

        income = (
            queryset.filter(transaction_type="income").aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )
        expenses = (
            queryset.filter(transaction_type="expense").aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )

        return Response(
            {
                "total_income": income,
                "total_expenses": expenses,
                "net": income - expenses,
            }
        )

    @action(detail=False, methods=["get"])
    def by_category(self, request):
        """
        Get transactions grouped by category.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Group by category
        categories = {}
        for transaction in queryset:
            category_name = (
                transaction.category.name if transaction.category else "Uncategorized"
            )
            if category_name not in categories:
                categories[category_name] = {
                    "category": category_name,
                    "total": 0,
                    "count": 0,
                }
            categories[category_name]["total"] += float(transaction.amount)
            categories[category_name]["count"] += 1

        return Response(list(categories.values()))
