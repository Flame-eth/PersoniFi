import graphene
from django.contrib.auth import get_user_model

from ..types.users import UserType

User = get_user_model()


class UserQueries(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.UUID())
    users = graphene.List(UserType)

    def resolve_user(self, info, id):
        if not info.context.user.is_authenticated:
            return None
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None

    def resolve_users(self, info):
        if not info.context.user.is_authenticated:
            return []
        # Only return the current user
        return [info.context.user]
