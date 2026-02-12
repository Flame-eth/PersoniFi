import django_filters

from apps.transactions.models import Transaction
from apps.accounts.models import Account
from apps.budgets.models import Budget
from apps.goals.models import Goal


class TransactionFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    amount_min = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_max = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = [
            "transaction_type",
            "currency",
            "payment_method",
            "account",
            "category",
        ]


class AccountFilter(django_filters.FilterSet):
    class Meta:
        model = Account
        fields = ["account_type", "currency", "is_active"]


class BudgetFilter(django_filters.FilterSet):
    class Meta:
        model = Budget
        fields = ["currency", "is_active"]


class GoalFilter(django_filters.FilterSet):
    class Meta:
        model = Goal
        fields = ["goal_type", "currency", "is_achieved"]
