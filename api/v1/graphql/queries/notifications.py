import graphene
from apps.notifications.models import Notification
from ..types.notifications import NotificationType
from ..authentication import login_required


class NotificationQueries(graphene.ObjectType):
    notification = graphene.Field(NotificationType, id=graphene.UUID())
    notifications = graphene.List(NotificationType, is_read=graphene.Boolean())

    @login_required
    def resolve_notification(self, info, id):
        """Retrieve a specific notification by ID (user must own it)."""
        try:
            return Notification.objects.get(pk=id, user=info.context.user)
        except Notification.DoesNotExist:
            return None

    @login_required
    def resolve_notifications(self, info, is_read=None):
        """Retrieve all notifications for the authenticated user."""
        queryset = Notification.objects.filter(user=info.context.user)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read)
        return queryset.order_by("-created_at")
