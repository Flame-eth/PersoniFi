from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Category


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "category_type", "is_system", "is_active", "created_at")
    list_filter = ("category_type", "is_system", "is_active", "created_at")
    search_fields = ("name",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
