import pytest
from django.contrib.auth import get_user_model
from tests.factories import UserFactory, AuthUserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test suite for User model."""

    def test_user_creation(self):
        """Test that a user can be created."""
        user = UserFactory()
        assert user.id is not None
        assert user.email is not None
        assert user.first_name is not None

    def test_user_email_uniqueness(self):
        """Test that email is unique."""
        user = UserFactory(email="test@example.com")
        with pytest.raises(Exception):
            UserFactory(email="test@example.com")

    def test_user_password_hashing(self):
        """Test that password is properly hashed."""
        user = AuthUserFactory()
        assert user.check_password("testpass123")
        assert not user.check_password("wrongpassword")

    def test_user_str_representation(self):
        """Test user string representation."""
        user = UserFactory(email="test@example.com")
        assert str(user) == user.email

    def test_user_phone_number(self):
        """Test that user can have phone number."""
        user = UserFactory()
        assert user.phone_number is not None

    def test_user_first_and_last_names(self):
        """Test that user has first and last names."""
        user = UserFactory(first_name="John", last_name="Doe")
        assert user.first_name == "John"
        assert user.last_name == "Doe"

    def test_user_active_by_default(self):
        """Test that users are active by default."""
        user = UserFactory()
        assert user.is_active is True

    def test_user_email_verified_by_default(self):
        """Test that user emails are verified by default in tests."""
        user = UserFactory()
        assert user.email_verified is True

    def test_user_with_multiple_queries(self):
        """Test creating multiple users."""
        users = [UserFactory() for _ in range(3)]
        assert len(users) == 3
        assert all(user.id is not None for user in users)


@pytest.mark.django_db
class TestUserAuthentication:
    """Test suite for User authentication."""

    def test_user_authentication(self, auth_user):
        """Test that user can authenticate."""
        assert auth_user.check_password("testpass123")

    def test_user_password_set(self, auth_user):
        """Test that password can be set."""
        auth_user.set_password("newpassword123")
        auth_user.save()
        assert auth_user.check_password("newpassword123")
        assert not auth_user.check_password("testpass123")

    def test_invalid_password(self, auth_user):
        """Test that invalid password fails."""
        assert not auth_user.check_password("wrongpassword")


@pytest.mark.django_db
class TestUserQuerySet:
    """Test suite for User QuerySet."""

    def test_user_count(self):
        """Test counting users."""
        UserFactory.create_batch(5)
        assert User.objects.count() == 5

    def test_user_filter_by_email(self):
        """Test filtering users by email."""
        user = UserFactory(email="unique@example.com")
        filtered = User.objects.filter(email="unique@example.com")
        assert filtered.count() == 1
        assert filtered.first() == user

    def test_user_filter_by_active(self):
        """Test filtering active users."""
        UserFactory(is_active=True)
        UserFactory(is_active=False)
        active_users = User.objects.filter(is_active=True)
        assert active_users.count() == 1
