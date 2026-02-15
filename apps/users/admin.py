from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from unfold.admin import ModelAdmin

from .models import User


@admin.register(User)
class UserAdmin(ModelAdmin, DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "preferred_currency",
                    "country",
                    "timezone",
                    "language",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
    list_display = ("email", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    ordering = ("-date_joined",)
    search_fields = ("email", "phone_number")
    date_hierarchy = "date_joined"
