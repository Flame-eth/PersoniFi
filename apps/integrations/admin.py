from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Integration, UserIntegration


@admin.register(Integration)
class IntegrationAdmin(ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(UserIntegration)
class UserIntegrationAdmin(ModelAdmin):
    list_display = ("user", "integration", "is_active", "created_at")
    list_filter = ("is_active", "integration", "created_at")
    search_fields = ("user__email", "integration__name")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
