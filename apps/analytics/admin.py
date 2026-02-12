from django.contrib import admin

from .models import FinancialSnapshot


@admin.register(FinancialSnapshot)
class FinancialSnapshotAdmin(admin.ModelAdmin):
    list_display = ("created_for_date", "total_income", "total_expense")
