from rest_framework import serializers

from apps.budgets.models import Budget, BudgetCategory


class BudgetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = [
            "id",
            "category",
            "allocated_amount",
            "alert_threshold",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BudgetSerializer(serializers.ModelSerializer):
    categories = BudgetCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Budget
        fields = [
            "id",
            "name",
            "total_amount",
            "currency",
            "start_date",
            "end_date",
            "is_active",
            "categories",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
