from rest_framework import serializers

from apps.transactions.models import Transaction
from .accounts import AccountSerializer
from .categories import CategorySerializer


class TransactionSerializer(serializers.ModelSerializer):
    account_detail = AccountSerializer(source="account", read_only=True)
    category_detail = CategorySerializer(source="category", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "account_detail",
            "category",
            "category_detail",
            "amount",
            "currency",
            "transaction_type",
            "date",
            "description",
            "notes",
            "payment_method",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_account(self, value):
        user = self.context["request"].user
        if value.user != user:
            raise serializers.ValidationError("Account does not belong to you")
        return value

    def validate_category(self, value):
        if value and not value.is_system:
            user = self.context["request"].user
            if value.user != user:
                raise serializers.ValidationError("Category does not belong to you")
        return value

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
