"""
Unfold Admin Configuration for PersoniFi

This module configures the Unfold admin interface with:
- Custom dashboard layout
- Financial overview cards
- Transaction statistics
- Budget tracking
"""

from django.apps import apps
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from unfold.admin import UnfoldModelAdmin


def index_view_extra_context(request):
    """
    Prepare extra context for admin index view with financial metrics.
    """
    User = apps.get_model("users", "User")
    Account = apps.get_model("accounts", "Account")
    Transaction = apps.get_model("transactions", "Transaction")
    Budget = apps.get_model("budgets", "Budget")
    Goal = apps.get_model("goals", "Goal")

    context = {
        "total_users": User.objects.filter(is_active=True).count(),
        "total_accounts": Account.objects.filter(is_active=True).count(),
        "recent_transactions": Transaction.objects.select_related(
            "account", "category"
        ).order_by("-date")[:5],
        "active_budgets": Budget.objects.filter(is_active=True).count(),
        "active_goals": Goal.objects.filter(is_achieved=False).count(),
    }

    return context
