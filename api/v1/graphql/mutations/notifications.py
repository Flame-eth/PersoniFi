import graphene
from apps.notifications.models import Notification
from ..authentication import login_required


class MarkNotificationRead(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    @login_required
    def mutate(mutate_self, info, id):
        """Mark a notification as read (user must own it)."""
        user = info.context.user

        try:
            notification = Notification.objects.get(pk=id, user=user)
            notification.is_read = True
            notification.save()
            return MarkNotificationRead(success=True, errors=[])
        except Notification.DoesNotExist:
            return MarkNotificationRead(
                success=False, errors=["Notification not found"]
            )
        except Exception as e:
            return MarkNotificationRead(success=False, errors=[str(e)])


class MarkAllNotificationsRead(graphene.Mutation):
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    @login_required
    def mutate(mutate_self, info):
        """Mark all notifications as read for the authenticated user."""
        user = info.context.user

        try:
            Notification.objects.filter(user=user).update(is_read=True)
            return MarkAllNotificationsRead(success=True, errors=[])
        except Exception as e:
            return MarkAllNotificationsRead(success=False, errors=[str(e)])
