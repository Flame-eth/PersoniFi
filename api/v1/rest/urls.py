from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    AccountViewSet,
    CategoryViewSet,
    TransactionViewSet,
    BudgetViewSet,
    BudgetCategoryViewSet,
    GoalViewSet,
    NotificationViewSet,
    AnalyticsViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"accounts", AccountViewSet, basename="account")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"budgets", BudgetViewSet, basename="budget")
router.register(r"budget-categories", BudgetCategoryViewSet, basename="budget-category")
router.register(r"goals", GoalViewSet, basename="goal")
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"analytics", AnalyticsViewSet, basename="analytics")

urlpatterns = [
    path("", include(router.urls)),
]
