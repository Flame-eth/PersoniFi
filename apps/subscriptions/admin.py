from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(ModelAdmin):
    list_display = ("name", "price", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ("user", "plan", "is_active", "start_date", "end_date", "created_at")
    list_filter = ("is_active", "plan", "start_date", "end_date", "created_at")
    search_fields = ("user__email", "plan__name")
    date_hierarchy = "start_date"
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-start_date",)
