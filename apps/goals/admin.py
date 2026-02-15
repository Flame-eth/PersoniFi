from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Goal


@admin.register(Goal)
class GoalAdmin(ModelAdmin):
    list_display = (
        "name",
        "target_amount",
        "currency",
        "deadline",
        "is_achieved",
        "created_at",
    )
    list_filter = ("currency", "is_achieved", "deadline", "created_at")
    search_fields = ("name",)
    date_hierarchy = "deadline"
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-deadline",)
