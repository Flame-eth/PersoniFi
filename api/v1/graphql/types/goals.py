import graphene
from graphene_django import DjangoObjectType

from apps.goals.models import Goal


class GoalType(DjangoObjectType):
    progress_percentage = graphene.Float()

    class Meta:
        model = Goal
        fields = (
            "id",
            "name",
            "target_amount",
            "current_amount",
            "currency",
            "deadline",
            "goal_type",
            "is_achieved",
            "created_at",
            "updated_at",
        )

    def resolve_progress_percentage(self, info):
        if self.target_amount > 0:
            return round((self.current_amount / self.target_amount) * 100, 2)
        return 0
