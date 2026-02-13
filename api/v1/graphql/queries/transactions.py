import graphene
from apps.transactions.models import Transaction
from ..types.transactions import TransactionType
from ..authentication import login_required


class TransactionQueries(graphene.ObjectType):
    transaction = graphene.Field(TransactionType, id=graphene.UUID())
    transactions = graphene.List(
        TransactionType,
        transaction_type=graphene.String(),
        account_id=graphene.UUID(),
        category_id=graphene.UUID(),
    )

    @login_required
    def resolve_transaction(self, info, id):
        """Retrieve a specific transaction by ID (user must own it)."""
        try:
            return Transaction.objects.get(pk=id, user=info.context.user)
        except Transaction.DoesNotExist:
            return None

    @login_required
    def resolve_transactions(
        self, info, transaction_type=None, account_id=None, category_id=None
    ):
        """Retrieve all transactions for the authenticated user."""
        queryset = Transaction.objects.filter(user=info.context.user)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        if account_id:
            queryset = queryset.filter(account_id=account_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset.order_by("-date", "-created_at")
