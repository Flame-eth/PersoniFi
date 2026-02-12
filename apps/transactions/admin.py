from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_type",
        "amount",
        "currency",
        "date",
        "account",
        "payment_method",
    )
    list_filter = ("transaction_type", "currency", "payment_method")
    search_fields = ("description", "notes")
