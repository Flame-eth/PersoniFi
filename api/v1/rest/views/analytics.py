from datetime import timedelta
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.transactions.models import Transaction
from apps.accounts.models import Account


class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for analytics and insights.
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def spending_trends(self, request):
        """
        Get spending trends over time (last 30 days by default).
        """
        days = int(request.query_params.get("days", 30))
        start_date = timezone.now().date() - timedelta(days=days)

        transactions = (
            Transaction.objects.filter(
                user=request.user,
                transaction_type="expense",
                date__gte=start_date,
            )
            .annotate(day=TruncDate("date"))
            .values("day")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("day")
        )

        return Response(list(transactions))

    @action(detail=False, methods=["get"])
    def category_breakdown(self, request):
        """
        Get spending breakdown by category.
        """
        days = int(request.query_params.get("days", 30))
        start_date = timezone.now().date() - timedelta(days=days)

        transactions = (
            Transaction.objects.filter(
                user=request.user,
                transaction_type="expense",
                date__gte=start_date,
            )
            .values("category__name")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
        )

        return Response(list(transactions))

    @action(detail=False, methods=["get"])
    def income_vs_expenses(self, request):
        """
        Get income vs expenses comparison.
        """
        days = int(request.query_params.get("days", 30))
        start_date = timezone.now().date() - timedelta(days=days)

        income = (
            Transaction.objects.filter(
                user=request.user,
                transaction_type="income",
                date__gte=start_date,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        expenses = (
            Transaction.objects.filter(
                user=request.user,
                transaction_type="expense",
                date__gte=start_date,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        return Response(
            {
                "income": income,
                "expenses": expenses,
                "net": income - expenses,
                "savings_rate": (
                    round(((income - expenses) / income) * 100, 2) if income > 0 else 0
                ),
            }
        )

    @action(detail=False, methods=["get"])
    def net_worth(self, request):
        """
        Calculate net worth based on all account balances.
        """
        accounts = Account.objects.filter(user=request.user, is_active=True)

        total_by_currency = {}
        for account in accounts:
            currency = account.currency
            if currency not in total_by_currency:
                total_by_currency[currency] = 0
            total_by_currency[currency] += float(account.balance)

        return Response(
            {
                "by_currency": total_by_currency,
                "accounts_count": accounts.count(),
            }
        )

    @action(detail=False, methods=["get"])
    def monthly_summary(self, request):
        """
        Get monthly summary for the last 6 months.
        """
        months = int(request.query_params.get("months", 6))
        start_date = timezone.now().date() - timedelta(days=months * 30)

        transactions = (
            Transaction.objects.filter(
                user=request.user,
                date__gte=start_date,
            )
            .annotate(month=TruncMonth("date"))
            .values("month", "transaction_type")
            .annotate(total=Sum("amount"))
            .order_by("month", "transaction_type")
        )

        # Organize by month
        monthly_data = {}
        for tx in transactions:
            month_key = tx["month"].strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "month": month_key,
                    "income": 0,
                    "expenses": 0,
                }

            if tx["transaction_type"] == "income":
                monthly_data[month_key]["income"] = float(tx["total"])
            else:
                monthly_data[month_key]["expenses"] = float(tx["total"])

        # Calculate net for each month
        for month_data in monthly_data.values():
            month_data["net"] = month_data["income"] - month_data["expenses"]

        return Response(list(monthly_data.values()))
