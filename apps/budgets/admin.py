from django.contrib import admin

from .models import Budget, BudgetCategory


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("name", "total_amount", "currency", "start_date", "end_date")
    list_filter = ("currency", "is_active")
    search_fields = ("name",)


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ("budget", "category", "allocated_amount", "alert_threshold")
    list_filter = ("budget", "category")
