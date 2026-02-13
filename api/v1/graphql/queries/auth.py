import graphene
from ..types.users import UserType
from ..authentication import login_required


class AuthQueries(graphene.ObjectType):
    me = graphene.Field(UserType)

    @login_required
    def resolve_me(self, info):
        """Return the current authenticated user."""
        return info.context.user
