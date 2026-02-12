import graphene
from apps.goals.models import Goal
from ..types.goals import GoalType


class GoalQueries(graphene.ObjectType):
    goal = graphene.Field(GoalType, id=graphene.UUID())
    goals = graphene.List(GoalType, is_achieved=graphene.Boolean())

    def resolve_goal(self, info, id):
        if not info.context.user.is_authenticated:
            return None
        try:
            return Goal.objects.get(pk=id, user=info.context.user)
        except Goal.DoesNotExist:
            return None

    def resolve_goals(self, info, is_achieved=None):
        if not info.context.user.is_authenticated:
            return []
        queryset = Goal.objects.filter(user=info.context.user)
        if is_achieved is not None:
            queryset = queryset.filter(is_achieved=is_achieved)
        return queryset.order_by("deadline")
