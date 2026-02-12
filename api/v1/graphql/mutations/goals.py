import graphene
from apps.goals.models import Goal
from ..types.goals import GoalType


class CreateGoal(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        target_amount = graphene.Decimal(required=True)
        currency = graphene.String(required=True)
        goal_type = graphene.String(required=True)
        deadline = graphene.Date()

    goal = graphene.Field(GoalType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, name, target_amount, currency, goal_type, deadline=None):
        user = info.context.user
        if not user.is_authenticated:
            return CreateGoal(success=False, errors=["Authentication required"])

        try:
            goal = Goal.objects.create(
                user=user,
                name=name,
                target_amount=target_amount,
                currency=currency,
                goal_type=goal_type,
                deadline=deadline,
            )
            return CreateGoal(success=True, goal=goal, errors=[])
        except Exception as e:
            return CreateGoal(success=False, errors=[str(e)])


class UpdateGoal(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        name = graphene.String()
        target_amount = graphene.Decimal()
        current_amount = graphene.Decimal()
        currency = graphene.String()
        goal_type = graphene.String()
        deadline = graphene.Date()
        is_achieved = graphene.Boolean()

    goal = graphene.Field(GoalType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(
        self,
        info,
        id,
        name=None,
        target_amount=None,
        current_amount=None,
        currency=None,
        goal_type=None,
        deadline=None,
        is_achieved=None,
    ):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateGoal(success=False, errors=["Authentication required"])

        try:
            goal = Goal.objects.get(pk=id, user=user)
            if name is not None:
                goal.name = name
            if target_amount is not None:
                goal.target_amount = target_amount
            if current_amount is not None:
                goal.current_amount = current_amount
            if currency is not None:
                goal.currency = currency
            if goal_type is not None:
                goal.goal_type = goal_type
            if deadline is not None:
                goal.deadline = deadline
            if is_achieved is not None:
                goal.is_achieved = is_achieved
            goal.save()
            return UpdateGoal(success=True, goal=goal, errors=[])
        except Goal.DoesNotExist:
            return UpdateGoal(success=False, errors=["Goal not found"])
        except Exception as e:
            return UpdateGoal(success=False, errors=[str(e)])


class DeleteGoal(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            return DeleteGoal(success=False, errors=["Authentication required"])

        try:
            goal = Goal.objects.get(pk=id, user=user)
            goal.delete()
            return DeleteGoal(success=True, errors=[])
        except Goal.DoesNotExist:
            return DeleteGoal(success=False, errors=["Goal not found"])
        except Exception as e:
            return DeleteGoal(success=False, errors=[str(e)])
