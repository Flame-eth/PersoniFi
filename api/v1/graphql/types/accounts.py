import graphene
from graphene_django import DjangoObjectType

from apps.accounts.models import Account


class AccountType(DjangoObjectType):
    class Meta:
        model = Account
        fields = (
            "id",
            "name",
            "account_type",
            "currency",
            "balance",
            "institution",
            "is_active",
            "created_at",
            "updated_at",
        )
