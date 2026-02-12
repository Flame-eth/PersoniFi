from django.conf import settings
from django.db import models

from apps.core.constants import CURRENCY_CHOICES
from apps.core.models import TimeStampedModel, UUIDModel


class Account(UUIDModel, TimeStampedModel):
    ACCOUNT_TYPES = (
        ("bank", "Bank"),
        ("mobile_money", "Mobile Money"),
        ("cash", "Cash"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts",
    )
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="NGN")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    institution = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.currency})"
