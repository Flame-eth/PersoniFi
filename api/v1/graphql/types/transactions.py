import graphene
from graphene_django import DjangoObjectType

from apps.transactions.models import Transaction


class TransactionType(DjangoObjectType):
    class Meta:
        model = Transaction
        fields = (
            "id",
            "account",
            "category",
            "amount",
            "currency",
            "transaction_type",
            "date",
            "description",
            "notes",
            "payment_method",
            "created_at",
            "updated_at",
        )
