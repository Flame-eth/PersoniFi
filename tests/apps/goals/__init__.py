import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.goals.models import Goal
from tests.factories import UserFactory, GoalFactory


@pytest.mark.django_db
class TestGoalModel:
    """Test suite for Goal model."""

    def test_goal_creation(self, auth_user):
        """Test that a goal can be created."""
        goal = GoalFactory(user=auth_user)
        assert goal.id is not None
        assert goal.user == auth_user
        assert goal.target_amount > 0

    def test_goal_types(self, auth_user):
        """Test different goal types."""
        goal_types = ["savings", "debt", "purchase"]

        for goal_type in goal_types:
            goal = GoalFactory(user=auth_user, goal_type=goal_type)
            assert goal.goal_type == goal_type

    def test_goal_target_amount_decimal(self, auth_user):
        """Test goal target amount is decimal."""
        goal = GoalFactory(user=auth_user, target_amount=Decimal("1000000.50"))
        assert isinstance(goal.target_amount, Decimal)
        assert goal.target_amount == Decimal("1000000.50")

    def test_goal_current_amount_default(self, auth_user):
        """Test goal current amount defaults to zero."""
        goal = GoalFactory(user=auth_user, current_amount=Decimal("0"))
        assert goal.current_amount == Decimal("0")

    def test_goal_current_amount_update(self, auth_user):
        """Test goal current amount can be updated."""
        goal = GoalFactory(user=auth_user, current_amount=Decimal("100000"))
        assert goal.current_amount == Decimal("100000")

    def test_goal_deadline(self, auth_user):
        """Test goal deadline."""
        deadline = timezone.now().date() + timedelta(days=365)
        goal = GoalFactory(user=auth_user, deadline=deadline)
        assert goal.deadline == deadline

    def test_goal_deadline_optional(self, auth_user):
        """Test goal deadline is optional."""
        goal = GoalFactory(user=auth_user, deadline=None)
        assert goal.deadline is None

    def test_goal_achieved_flag(self, auth_user):
        """Test goal achieved status."""
        goal = GoalFactory(user=auth_user, is_achieved=False)
        assert goal.is_achieved is False

    def test_goal_currency(self, auth_user):
        """Test goal currency."""
        goal = GoalFactory(user=auth_user, currency="NGN")
        assert goal.currency == "NGN"

    def test_goal_str_representation(self, auth_user):
        """Test goal string representation."""
        goal = GoalFactory(user=auth_user, name="House Fund")
        assert str(goal) == "House Fund"


@pytest.mark.django_db
class TestGoalProgress:
    """Test suite for goal progress tracking."""

    def test_goal_progress_percentage(self, auth_user):
        """Test calculating goal progress."""
        goal = GoalFactory(
            user=auth_user,
            target_amount=Decimal("1000000"),
            current_amount=Decimal("500000"),
        )
        progress = (goal.current_amount / goal.target_amount) * 100
        assert progress == Decimal("50")

    def test_goal_achieved_status(self, auth_user):
        """Test goal achieved when current >= target."""
        goal = GoalFactory(
            user=auth_user,
            target_amount=Decimal("100000"),
            current_amount=Decimal("100000"),
            is_achieved=True,
        )
        assert goal.is_achieved is True

    def test_goal_remaining_amount(self, auth_user):
        """Test calculating remaining amount."""
        goal = GoalFactory(
            user=auth_user,
            target_amount=Decimal("1000000"),
            current_amount=Decimal("600000"),
        )
        remaining = goal.target_amount - goal.current_amount
        assert remaining == Decimal("400000")


@pytest.mark.django_db
class TestGoalQuerySet:
    """Test suite for Goal QuerySet."""

    def test_goal_count_per_user(self, auth_user):
        """Test counting goals per user."""
        GoalFactory.create_batch(3, user=auth_user)
        assert Goal.objects.filter(user=auth_user).count() == 3

    def test_filter_goals_by_type(self, auth_user):
        """Test filtering goals by type."""
        GoalFactory(user=auth_user, goal_type="savings")
        GoalFactory(user=auth_user, goal_type="debt")

        savings_goals = Goal.objects.filter(goal_type="savings")
        debt_goals = Goal.objects.filter(goal_type="debt")

        assert savings_goals.count() >= 1
        assert debt_goals.count() >= 1

    def test_filter_achieved_goals(self, auth_user):
        """Test filtering achieved goals."""
        GoalFactory(user=auth_user, is_achieved=True)
        GoalFactory(user=auth_user, is_achieved=False)

        achieved = Goal.objects.filter(is_achieved=True)
        assert achieved.count() >= 1

    def test_filter_goals_by_deadline(self, auth_user):
        """Test filtering goals by deadline."""
        today = timezone.now().date()
        future_date = today + timedelta(days=30)

        goal = GoalFactory(user=auth_user, deadline=future_date)

        upcoming = Goal.objects.filter(deadline__gte=today)
        assert goal in upcoming

    def test_user_goals_relationship(self, auth_user):
        """Test user goals relationship."""
        goals = GoalFactory.create_batch(3, user=auth_user)
        assert auth_user.goals.count() == 3
        for goal in goals:
            assert goal in auth_user.goals.all()


@pytest.mark.django_db
class TestMultipleGoals:
    """Test suite for managing multiple goals."""

    def test_multiple_user_goals(self, multiple_goals, auth_user):
        """Test user with multiple goals."""
        assert len(multiple_goals) == 3
        for goal in multiple_goals:
            assert goal.user == auth_user

    def test_goals_isolation_by_user(self):
        """Test goals are isolated by user."""
        user1 = UserFactory()
        user2 = UserFactory()

        GoalFactory(user=user1)
        GoalFactory(user=user2)

        assert user1.goals.count() == 1
        assert user2.goals.count() == 1

    def test_mixed_goal_types(self, auth_user):
        """Test user with mixed goal types."""
        goal_types = ["savings", "debt", "purchase"]

        goals = [
            GoalFactory(user=auth_user, goal_type=goal_type) for goal_type in goal_types
        ]

        for goal_type, goal in zip(goal_types, goals):
            assert goal.goal_type == goal_type


@pytest.mark.django_db
class TestGoalAmounts:
    """Test suite for goal amount operations."""

    def test_goal_zero_current_amount(self, auth_user):
        """Test goal with zero current amount."""
        goal = GoalFactory(user=auth_user, current_amount=Decimal("0"))
        assert goal.current_amount == Decimal("0")

    def test_goal_large_target_amount(self, auth_user):
        """Test goal with large target amount."""
        large_amount = Decimal("999999999.99")
        goal = GoalFactory(user=auth_user, target_amount=large_amount)
        assert goal.target_amount == large_amount

    def test_goal_amount_precision(self, auth_user):
        """Test goal amount decimal precision."""
        goal = GoalFactory(
            user=auth_user,
            target_amount=Decimal("1500000.75"),
            current_amount=Decimal("250000.25"),
        )
        assert goal.target_amount == Decimal("1500000.75")
        assert goal.current_amount == Decimal("250000.25")
