from django.conf import settings
from django.db import models

from apps.core.constants import CURRENCY_CHOICES
from apps.core.models import TimeStampedModel, UUIDModel
from apps.categories.models import Category


class Budget(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budgets",
    )
    name = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="NGN")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class BudgetCategory(UUIDModel, TimeStampedModel):
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="budget_categories",
    )
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2)
    alert_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=0.8)

    def __str__(self):
        return f"{self.budget.name}: {self.category.name}"
