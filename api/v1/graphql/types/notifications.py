import graphene
from graphene_django import DjangoObjectType

from apps.notifications.models import Notification


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = (
            "id",
            "title",
            "message",
            "is_read",
            "created_at",
            "updated_at",
        )
