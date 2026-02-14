import factory
from django.contrib.auth import get_user_model
from faker import Faker

fake = Faker()
User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test User instances."""

    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.LazyAttribute(lambda _: fake.email())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    phone_number = factory.LazyAttribute(lambda _: fake.phone_number())
    is_active = True
    email_verified = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password after user creation."""
        if create:
            # Use a default password for testing
            obj.set_password("testpass123")
            obj.save()
        if extracted:
            obj.set_password(extracted)
            obj.save()


class AuthUserFactory(UserFactory):
    """Factory for authenticated users with verified emails."""

    is_active = True
    email_verified = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Ensure password is set."""
        if create or not obj.check_password("testpass123"):
            obj.set_password("testpass123")
            obj.save()
