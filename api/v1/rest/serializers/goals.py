from rest_framework import serializers

from apps.goals.models import Goal


class GoalSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = [
            "id",
            "name",
            "target_amount",
            "current_amount",
            "currency",
            "deadline",
            "goal_type",
            "is_achieved",
            "progress_percentage",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_progress_percentage(self, obj):
        if obj.target_amount > 0:
            return round((obj.current_amount / obj.target_amount) * 100, 2)
        return 0

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
