from django.contrib import admin

from .models import Integration, UserIntegration


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)


@admin.register(UserIntegration)
class UserIntegrationAdmin(admin.ModelAdmin):
    list_display = ("user", "integration", "is_active")
    list_filter = ("is_active", "integration")
