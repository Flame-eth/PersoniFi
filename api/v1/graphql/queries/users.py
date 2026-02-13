import graphene
from django.contrib.auth import get_user_model

from ..types.users import UserType
from ..authentication import login_required

User = get_user_model()


class UserQueries(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.UUID())
    users = graphene.List(UserType)

    @login_required
    def resolve_user(self, info, id):
        """Retrieve current authenticated user (only your own data)."""
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None

    @login_required
    def resolve_users(self, info):
        """Retrieve current authenticated user (only your own data)."""
        # Only return the current user
        return [info.context.user]
