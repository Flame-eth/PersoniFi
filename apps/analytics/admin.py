from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import FinancialSnapshot


@admin.register(FinancialSnapshot)
class FinancialSnapshotAdmin(ModelAdmin):
    list_display = ("created_for_date", "total_income", "total_expense", "created_at")
    list_filter = ("created_at", "created_for_date")
    date_hierarchy = "created_for_date"
    readonly_fields = ("created_at",)
    ordering = ("-created_for_date",)
