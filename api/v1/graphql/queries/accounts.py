import graphene
from apps.accounts.models import Account
from ..types.accounts import AccountType


class AccountQueries(graphene.ObjectType):
    account = graphene.Field(AccountType, id=graphene.UUID())
    accounts = graphene.List(AccountType, is_active=graphene.Boolean())

    def resolve_account(self, info, id):
        if not info.context.user.is_authenticated:
            return None
        try:
            return Account.objects.get(pk=id, user=info.context.user)
        except Account.DoesNotExist:
            return None

    def resolve_accounts(self, info, is_active=None):
        if not info.context.user.is_authenticated:
            return []
        queryset = Account.objects.filter(user=info.context.user)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset
