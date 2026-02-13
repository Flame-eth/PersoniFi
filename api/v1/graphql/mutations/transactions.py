import graphene
from datetime import datetime
from apps.transactions.models import Transaction
from ..types.transactions import TransactionType
from ..authentication import login_required


class CreateTransaction(graphene.Mutation):
    class Arguments:
        account_id = graphene.UUID(required=True)
        category_id = graphene.UUID()
        amount = graphene.Decimal(required=True)
        currency = graphene.String(required=True)
        transaction_type = graphene.String(required=True)
        date = graphene.Date()
        description = graphene.String()
        notes = graphene.String()
        payment_method = graphene.String(required=True)

    transaction = graphene.Field(TransactionType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    @login_required
    def mutate(
        mutate_self,
        info,
        account_id,
        amount,
        currency,
        transaction_type,
        payment_method,
        category_id=None,
        date=None,
        description=None,
        notes=None,
    ):
        """Create a new transaction for the authenticated user."""
        user = info.context.user

        try:
            transaction = Transaction.objects.create(
                user=user,
                account_id=account_id,
                category_id=category_id,
                amount=amount,
                currency=currency,
                transaction_type=transaction_type,
                date=date or datetime.now().date(),
                description=description or "",
                notes=notes or "",
                payment_method=payment_method,
            )
            return CreateTransaction(success=True, transaction=transaction, errors=[])
        except Exception as e:
            return CreateTransaction(success=False, errors=[str(e)])


class UpdateTransaction(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        account_id = graphene.UUID()
        category_id = graphene.UUID()
        amount = graphene.Decimal()
        currency = graphene.String()
        transaction_type = graphene.String()
        date = graphene.Date()
        description = graphene.String()
        notes = graphene.String()
        payment_method = graphene.String()

    transaction = graphene.Field(TransactionType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    @login_required
    def mutate(
        mutate_self,
        info,
        id,
        account_id=None,
        category_id=None,
        amount=None,
        currency=None,
        transaction_type=None,
        date=None,
        description=None,
        notes=None,
        payment_method=None,
    ):
        """Update a transaction (user must own it)."""
        user = info.context.user

        try:
            transaction = Transaction.objects.get(pk=id, user=user)
            if account_id is not None:
                transaction.account_id = account_id
            if category_id is not None:
                transaction.category_id = category_id
            if amount is not None:
                transaction.amount = amount
            if currency is not None:
                transaction.currency = currency
            if transaction_type is not None:
                transaction.transaction_type = transaction_type
            if date is not None:
                transaction.date = date
            if description is not None:
                transaction.description = description
            if notes is not None:
                transaction.notes = notes
            if payment_method is not None:
                transaction.payment_method = payment_method
            transaction.save()
            return UpdateTransaction(success=True, transaction=transaction, errors=[])
        except Transaction.DoesNotExist:
            return UpdateTransaction(success=False, errors=["Transaction not found"])
        except Exception as e:
            return UpdateTransaction(success=False, errors=[str(e)])


class DeleteTransaction(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    @login_required
    def mutate(mutate_self, info, id):
        """Delete a transaction (user must own it)."""
        user = info.context.user

        try:
            transaction = Transaction.objects.get(pk=id, user=user)
            transaction.delete()
            return DeleteTransaction(success=True, errors=[])
        except Transaction.DoesNotExist:
            return DeleteTransaction(success=False, errors=["Transaction not found"])
        except Exception as e:
            return DeleteTransaction(success=False, errors=[str(e)])
