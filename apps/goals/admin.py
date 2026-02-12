from django.contrib import admin

from .models import Goal


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("name", "target_amount", "currency", "deadline", "is_achieved")
    list_filter = ("currency", "is_achieved")
    search_fields = ("name",)
