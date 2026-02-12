import graphene
from apps.notifications.models import Notification
from ..types.notifications import NotificationType


class NotificationQueries(graphene.ObjectType):
    notification = graphene.Field(NotificationType, id=graphene.UUID())
    notifications = graphene.List(NotificationType, is_read=graphene.Boolean())

    def resolve_notification(self, info, id):
        if not info.context.user.is_authenticated:
            return None
        try:
            return Notification.objects.get(pk=id, user=info.context.user)
        except Notification.DoesNotExist:
            return None

    def resolve_notifications(self, info, is_read=None):
        if not info.context.user.is_authenticated:
            return []
        queryset = Notification.objects.filter(user=info.context.user)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read)
        return queryset.order_by("-created_at")
