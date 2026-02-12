from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel


class Notification(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=120)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title
