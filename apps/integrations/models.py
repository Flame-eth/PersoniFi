from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel


class Integration(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class UserIntegration(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="integrations",
    )
    integration = models.ForeignKey(
        Integration,
        on_delete=models.CASCADE,
        related_name="user_integrations",
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} - {self.integration.name}"
