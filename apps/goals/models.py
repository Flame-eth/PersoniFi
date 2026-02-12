from django.conf import settings
from django.db import models

from apps.core.constants import CURRENCY_CHOICES
from apps.core.models import TimeStampedModel, UUIDModel


class Goal(UUIDModel, TimeStampedModel):
    GOAL_TYPES = (
        ("savings", "Savings"),
        ("debt", "Debt Payoff"),
        ("purchase", "Planned Purchase"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="goals",
    )
    name = models.CharField(max_length=120)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    current_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="NGN")
    deadline = models.DateField(null=True, blank=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    is_achieved = models.BooleanField(default=False)

    def __str__(self):
        return self.name
