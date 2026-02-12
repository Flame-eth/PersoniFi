import graphene

from .queries import (
    AuthQueries,
    UserQueries,
    AccountQueries,
    CategoryQueries,
    TransactionQueries,
    BudgetQueries,
    GoalQueries,
    NotificationQueries,
)
from .mutations import (
    CreateAccount,
    UpdateAccount,
    DeleteAccount,
    CreateCategory,
    UpdateCategory,
    DeleteCategory,
    CreateTransaction,
    UpdateTransaction,
    DeleteTransaction,
    CreateBudget,
    UpdateBudget,
    DeleteBudget,
    CreateGoal,
    UpdateGoal,
    DeleteGoal,
    MarkNotificationRead,
    MarkAllNotificationsRead,
)


class Query(
    AuthQueries,
    UserQueries,
    AccountQueries,
    CategoryQueries,
    TransactionQueries,
    BudgetQueries,
    GoalQueries,
    NotificationQueries,
    graphene.ObjectType,
):
    pass


class Mutation(graphene.ObjectType):
    # Account mutations
    create_account = CreateAccount.Field()
    update_account = UpdateAccount.Field()
    delete_account = DeleteAccount.Field()

    # Category mutations
    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()

    # Transaction mutations
    create_transaction = CreateTransaction.Field()
    update_transaction = UpdateTransaction.Field()
    delete_transaction = DeleteTransaction.Field()

    # Budget mutations
    create_budget = CreateBudget.Field()
    update_budget = UpdateBudget.Field()
    delete_budget = DeleteBudget.Field()

    # Goal mutations
    create_goal = CreateGoal.Field()
    update_goal = UpdateGoal.Field()
    delete_goal = DeleteGoal.Field()

    # Notification mutations
    mark_notification_read = MarkNotificationRead.Field()
    mark_all_notifications_read = MarkAllNotificationsRead.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
