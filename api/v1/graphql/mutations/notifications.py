import graphene
from apps.notifications.models import Notification


class MarkNotificationRead(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            return MarkNotificationRead(
                success=False, errors=["Authentication required"]
            )

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

    def mutate(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return MarkAllNotificationsRead(
                success=False, errors=["Authentication required"]
            )

        try:
            Notification.objects.filter(user=user).update(is_read=True)
            return MarkAllNotificationsRead(success=True, errors=[])
        except Exception as e:
            return MarkAllNotificationsRead(success=False, errors=[str(e)])
