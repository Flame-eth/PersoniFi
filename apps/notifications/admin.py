from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ("title", "is_read", "user", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("title", "message")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
