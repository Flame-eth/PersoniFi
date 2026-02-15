from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Budget, BudgetCategory


class BudgetCategoryInline(TabularInline):
    model = BudgetCategory
    extra = 1
    fields = ("category", "allocated_amount", "alert_threshold")


@admin.register(Budget)
class BudgetAdmin(ModelAdmin):
    list_display = (
        "name",
        "total_amount",
        "currency",
        "start_date",
        "end_date",
        "is_active",
        "created_at",
    )
    list_filter = ("currency", "is_active", "start_date", "end_date", "created_at")
    search_fields = ("name",)
    date_hierarchy = "start_date"
    readonly_fields = ("created_at", "updated_at")
    inlines = [BudgetCategoryInline]
    ordering = ("-start_date",)


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(ModelAdmin):
    list_display = (
        "budget",
        "category",
        "allocated_amount",
        "alert_threshold",
        "created_at",
    )
    list_filter = ("budget", "category", "created_at")
    search_fields = ("budget__name", "category__name")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
