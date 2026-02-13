import graphene
from apps.goals.models import Goal
from ..types.goals import GoalType
from ..authentication import login_required


class GoalQueries(graphene.ObjectType):
    goal = graphene.Field(GoalType, id=graphene.UUID())
    goals = graphene.List(GoalType, is_achieved=graphene.Boolean())

    @login_required
    def resolve_goal(self, info, id):
        """Retrieve a specific goal by ID. User must own the goal."""
        try:
            return Goal.objects.get(pk=id, user=info.context.user)
        except Goal.DoesNotExist:
            return None

    @login_required
    def resolve_goals(self, info, is_achieved=None):
        """Retrieve all goals for the authenticated user."""
        queryset = Goal.objects.filter(user=info.context.user)
        if is_achieved is not None:
            queryset = queryset.filter(is_achieved=is_achieved)
        return queryset.order_by("deadline")
