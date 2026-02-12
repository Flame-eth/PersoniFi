from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.constants import CURRENCY_CHOICES
from apps.core.models import TimeStampedModel, UUIDModel
from apps.accounts.models import Account
from apps.categories.models import Category


class Transaction(UUIDModel, TimeStampedModel):
    TRANSACTION_TYPES = (
        ("income", "Income"),
        ("expense", "Expense"),
    )
    PAYMENT_METHODS = (
        ("cash", "Cash"),
        ("mobile_money", "Mobile Money"),
        ("bank_transfer", "Bank Transfer"),
        ("card", "Card"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="NGN")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)

    def __str__(self):
        return f"{self.transaction_type} {self.amount} {self.currency}"
