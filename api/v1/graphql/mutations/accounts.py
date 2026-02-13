import graphene
from apps.accounts.models import Account
from ..types.accounts import AccountType
from ..authentication import login_required


class CreateAccount(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        account_type = graphene.String(required=True)
        currency = graphene.String(required=True)
        institution = graphene.String()

    account = graphene.Field(AccountType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    @login_required
    def mutate(mutate_self, info, name, account_type, currency, institution=None):
        """Create a new account for the authenticated user."""
        user = info.context.user
        try:
            account = Account.objects.create(
                user=user,
                name=name,
                account_type=account_type,
                currency=currency,
                institution=institution or "",
            )
            return CreateAccount(success=True, account=account, errors=[])
        except Exception as e:
            return CreateAccount(success=False, errors=[str(e)])


class UpdateAccount(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        name = graphene.String()
        account_type = graphene.String()
        currency = graphene.String()
        institution = graphene.String()
        is_active = graphene.Boolean()

    account = graphene.Field(AccountType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    @login_required
    def mutate(
        mutate_self,
        info,
        id,
        name=None,
        account_type=None,
        currency=None,
        institution=None,
        is_active=None,
    ):
        """Update an account (user must own the account)."""
        user = info.context.user
        try:
            account = Account.objects.get(pk=id, user=user)
            if name is not None:
                account.name = name
            if account_type is not None:
                account.account_type = account_type
            if currency is not None:
                account.currency = currency
            if institution is not None:
                account.institution = institution
            if is_active is not None:
                account.is_active = is_active
            account.save()
            return UpdateAccount(success=True, account=account, errors=[])
        except Account.DoesNotExist:
            return UpdateAccount(success=False, errors=["Account not found"])
        except Exception as e:
            return UpdateAccount(success=False, errors=[str(e)])


class DeleteAccount(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    @login_required
    def mutate(mutate_self, info, id):
        """Delete an account (user must own the account)."""
        user = info.context.user
        try:
            account = Account.objects.get(pk=id, user=user)
            account.delete()
            return DeleteAccount(success=True, errors=[])
        except Account.DoesNotExist:
            return DeleteAccount(success=False, errors=["Account not found"])
        except Exception as e:
            return DeleteAccount(success=False, errors=[str(e)])


class DeleteAccount(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            return DeleteAccount(success=False, errors=["Authentication required"])

        try:
            account = Account.objects.get(pk=id, user=user)
            account.delete()
            return DeleteAccount(success=True, errors=[])
        except Account.DoesNotExist:
            return DeleteAccount(success=False, errors=["Account not found"])
        except Exception as e:
            return DeleteAccount(success=False, errors=[str(e)])
