from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel


class FinancialSnapshot(UUIDModel, TimeStampedModel):
    created_for_date = models.DateField()
    total_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expense = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return str(self.created_for_date)
