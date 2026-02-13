import graphene
from apps.accounts.models import Account
from ..types.accounts import AccountType
from ..authentication import login_required


class AccountQueries(graphene.ObjectType):
    account = graphene.Field(AccountType, id=graphene.UUID())
    accounts = graphene.List(AccountType, is_active=graphene.Boolean())

    @login_required
    def resolve_account(self, info, id):
        """Retrieve a specific account by ID (user must own it)."""
        try:
            return Account.objects.get(pk=id, user=info.context.user)
        except Account.DoesNotExist:
            return None

    @login_required
    def resolve_accounts(self, info, is_active=None):
        """Retrieve all accounts for the authenticated user."""
        queryset = Account.objects.filter(user=info.context.user)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset
