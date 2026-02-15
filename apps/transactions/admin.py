from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = (
        "transaction_type",
        "amount",
        "currency",
        "date",
        "account",
        "payment_method",
        "created_at",
    )
    list_filter = (
        "transaction_type",
        "currency",
        "payment_method",
        "date",
        "created_at",
    )
    search_fields = ("description", "notes")
    date_hierarchy = "date"
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-date",)
