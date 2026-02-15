from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Account


@admin.register(Account)
class AccountAdmin(ModelAdmin):
    list_display = (
        "name",
        "account_type",
        "currency",
        "balance",
        "is_active",
        "created_at",
    )
    list_filter = ("account_type", "currency", "is_active", "created_at")
    search_fields = ("name", "institution")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
