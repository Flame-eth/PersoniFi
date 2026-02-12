import graphene
from apps.budgets.models import Budget
from ..types.budgets import BudgetType


class CreateBudget(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        total_amount = graphene.Decimal(required=True)
        currency = graphene.String(required=True)
        start_date = graphene.Date(required=True)
        end_date = graphene.Date(required=True)

    budget = graphene.Field(BudgetType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, name, total_amount, currency, start_date, end_date):
        user = info.context.user
        if not user.is_authenticated:
            return CreateBudget(success=False, errors=["Authentication required"])

        try:
            budget = Budget.objects.create(
                user=user,
                name=name,
                total_amount=total_amount,
                currency=currency,
                start_date=start_date,
                end_date=end_date,
            )
            return CreateBudget(success=True, budget=budget, errors=[])
        except Exception as e:
            return CreateBudget(success=False, errors=[str(e)])


class UpdateBudget(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        name = graphene.String()
        total_amount = graphene.Decimal()
        currency = graphene.String()
        start_date = graphene.Date()
        end_date = graphene.Date()
        is_active = graphene.Boolean()

    budget = graphene.Field(BudgetType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(
        self,
        info,
        id,
        name=None,
        total_amount=None,
        currency=None,
        start_date=None,
        end_date=None,
        is_active=None,
    ):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateBudget(success=False, errors=["Authentication required"])

        try:
            budget = Budget.objects.get(pk=id, user=user)
            if name is not None:
                budget.name = name
            if total_amount is not None:
                budget.total_amount = total_amount
            if currency is not None:
                budget.currency = currency
            if start_date is not None:
                budget.start_date = start_date
            if end_date is not None:
                budget.end_date = end_date
            if is_active is not None:
                budget.is_active = is_active
            budget.save()
            return UpdateBudget(success=True, budget=budget, errors=[])
        except Budget.DoesNotExist:
            return UpdateBudget(success=False, errors=["Budget not found"])
        except Exception as e:
            return UpdateBudget(success=False, errors=[str(e)])


class DeleteBudget(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            return DeleteBudget(success=False, errors=["Authentication required"])

        try:
            budget = Budget.objects.get(pk=id, user=user)
            budget.delete()
            return DeleteBudget(success=True, errors=[])
        except Budget.DoesNotExist:
            return DeleteBudget(success=False, errors=["Budget not found"])
        except Exception as e:
            return DeleteBudget(success=False, errors=[str(e)])
