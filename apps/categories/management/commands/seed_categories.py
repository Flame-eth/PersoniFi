from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.categories.models import Category

User = get_user_model()


class Command(BaseCommand):
    help = "Seed default system categories for personal finance management"

    def handle(self, *args, **options):
        # System categories - available to all users
        categories_data = [
            # Income Categories
            {
                "name": "Salary",
                "type": "income",
                "icon": "💼",
                "color": "#10B981",
                "is_system": True,
                "description": "Monthly salary and wages",
            },
            {
                "name": "Business Income",
                "type": "income",
                "icon": "💰",
                "color": "#059669",
                "is_system": True,
                "description": "Income from business activities",
            },
            {
                "name": "Investments",
                "type": "income",
                "icon": "📈",
                "color": "#34D399",
                "is_system": True,
                "description": "Returns from investments",
            },
            {
                "name": "Freelance",
                "type": "income",
                "icon": "🎯",
                "color": "#6EE7B7",
                "is_system": True,
                "description": "Freelance and contract work",
            },
            {
                "name": "Gifts",
                "type": "income",
                "icon": "🎁",
                "color": "#A7F3D0",
                "is_system": True,
                "description": "Monetary gifts received",
            },
            {
                "name": "Other Income",
                "type": "income",
                "icon": "💵",
                "color": "#D1FAE5",
                "is_system": True,
                "description": "Other sources of income",
            },
            # Expense Categories - Essential
            {
                "name": "Housing",
                "type": "expense",
                "icon": "🏠",
                "color": "#EF4444",
                "is_system": True,
                "description": "Rent, mortgage, and housing expenses",
            },
            {
                "name": "Utilities",
                "type": "expense",
                "icon": "⚡",
                "color": "#DC2626",
                "is_system": True,
                "description": "Electricity, water, gas, internet",
            },
            {
                "name": "Food & Groceries",
                "type": "expense",
                "icon": "🍽️",
                "color": "#F59E0B",
                "is_system": True,
                "description": "Groceries and food items",
            },
            {
                "name": "Transportation",
                "type": "expense",
                "icon": "🚗",
                "color": "#F97316",
                "is_system": True,
                "description": "Fuel, public transport, vehicle maintenance",
            },
            {
                "name": "Healthcare",
                "type": "expense",
                "icon": "⚕️",
                "color": "#EF4444",
                "is_system": True,
                "description": "Medical expenses and insurance",
            },
            {
                "name": "Education",
                "type": "expense",
                "icon": "📚",
                "color": "#3B82F6",
                "is_system": True,
                "description": "School fees, courses, books",
            },
            # Expense Categories - Lifestyle
            {
                "name": "Entertainment",
                "type": "expense",
                "icon": "🎬",
                "color": "#8B5CF6",
                "is_system": True,
                "description": "Movies, events, hobbies",
            },
            {
                "name": "Dining Out",
                "type": "expense",
                "icon": "🍴",
                "color": "#EC4899",
                "is_system": True,
                "description": "Restaurants and takeout",
            },
            {
                "name": "Shopping",
                "type": "expense",
                "icon": "🛍️",
                "color": "#6366F1",
                "is_system": True,
                "description": "Clothing, accessories, personal items",
            },
            {
                "name": "Personal Care",
                "type": "expense",
                "icon": "💅",
                "color": "#EC4899",
                "is_system": True,
                "description": "Salon, spa, grooming",
            },
            {
                "name": "Gifts & Donations",
                "type": "expense",
                "icon": "🎁",
                "color": "#14B8A6",
                "is_system": True,
                "description": "Gifts given and charitable donations",
            },
            {
                "name": "Subscriptions",
                "type": "expense",
                "icon": "📱",
                "color": "#6366F1",
                "is_system": True,
                "description": "Digital services and memberships",
            },
            # Expense Categories - Financial
            {
                "name": "Insurance",
                "type": "expense",
                "icon": "🛡️",
                "color": "#1F2937",
                "is_system": True,
                "description": "Insurance premiums",
            },
            {
                "name": "Debt Payment",
                "type": "expense",
                "icon": "💳",
                "color": "#6B7280",
                "is_system": True,
                "description": "Loan repayments and credit card bills",
            },
            {
                "name": "Savings",
                "type": "expense",
                "icon": "🏦",
                "color": "#10B981",
                "is_system": True,
                "description": "Transfer to savings accounts",
            },
            {
                "name": "Investments",
                "type": "expense",
                "icon": "📊",
                "color": "#059669",
                "is_system": True,
                "description": "Investment contributions",
            },
            {
                "name": "Taxes",
                "type": "expense",
                "icon": "📋",
                "color": "#4B5563",
                "is_system": True,
                "description": "Tax payments",
            },
            # Expense Categories - Other
            {
                "name": "Travel",
                "type": "expense",
                "icon": "✈️",
                "color": "#06B6D4",
                "is_system": True,
                "description": "Vacation and travel expenses",
            },
            {
                "name": "Pets",
                "type": "expense",
                "icon": "🐾",
                "color": "#F59E0B",
                "is_system": True,
                "description": "Pet food, vet, and pet care",
            },
            {
                "name": "Children",
                "type": "expense",
                "icon": "👶",
                "color": "#EC4899",
                "is_system": True,
                "description": "Childcare and children expenses",
            },
            {
                "name": "Other Expenses",
                "type": "expense",
                "icon": "📦",
                "color": "#9CA3AF",
                "is_system": True,
                "description": "Miscellaneous expenses",
            },
        ]

        created_count = 0
        updated_count = 0

        for category_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=category_data["name"],
                type=category_data["type"],
                is_system=True,
                defaults={
                    "icon": category_data.get("icon", ""),
                    "color": category_data.get("color", "#6B7280"),
                    "description": category_data.get("description", ""),
                    "user": None,  # System categories have no user
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created system category: {category.name}")
                )
            else:
                # Update existing category with new data
                category.icon = category_data.get("icon", category.icon)
                category.color = category_data.get("color", category.color)
                category.description = category_data.get(
                    "description", category.description
                )
                category.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"↻ Updated system category: {category.name}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Seeding complete! Created: {created_count}, Updated: {updated_count}"
            )
        )
