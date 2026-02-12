import graphene
from apps.categories.models import Category
from ..types.categories import CategoryType


class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        category_type = graphene.String(required=True)
        parent_id = graphene.UUID()

    category = graphene.Field(CategoryType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, name, category_type, parent_id=None):
        user = info.context.user
        if not user.is_authenticated:
            return CreateCategory(success=False, errors=["Authentication required"])

        try:
            category = Category.objects.create(
                user=user,
                name=name,
                category_type=category_type,
                parent_id=parent_id,
            )
            return CreateCategory(success=True, category=category, errors=[])
        except Exception as e:
            return CreateCategory(success=False, errors=[str(e)])


class UpdateCategory(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        name = graphene.String()
        category_type = graphene.String()
        parent_id = graphene.UUID()
        is_active = graphene.Boolean()

    category = graphene.Field(CategoryType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(
        self, info, id, name=None, category_type=None, parent_id=None, is_active=None
    ):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateCategory(success=False, errors=["Authentication required"])

        try:
            category = Category.objects.get(pk=id, user=user)
            if category.is_system:
                return UpdateCategory(
                    success=False, errors=["Cannot update system categories"]
                )
            if name is not None:
                category.name = name
            if category_type is not None:
                category.category_type = category_type
            if parent_id is not None:
                category.parent_id = parent_id
            if is_active is not None:
                category.is_active = is_active
            category.save()
            return UpdateCategory(success=True, category=category, errors=[])
        except Category.DoesNotExist:
            return UpdateCategory(success=False, errors=["Category not found"])
        except Exception as e:
            return UpdateCategory(success=False, errors=[str(e)])


class DeleteCategory(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            return DeleteCategory(success=False, errors=["Authentication required"])

        try:
            category = Category.objects.get(pk=id, user=user)
            if category.is_system:
                return DeleteCategory(
                    success=False, errors=["Cannot delete system categories"]
                )
            category.is_active = False
            category.save()
            return DeleteCategory(success=True, errors=[])
        except Category.DoesNotExist:
            return DeleteCategory(success=False, errors=["Category not found"])
        except Exception as e:
            return DeleteCategory(success=False, errors=[str(e)])
