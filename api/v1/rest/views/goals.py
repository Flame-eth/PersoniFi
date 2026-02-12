from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.goals.models import Goal
from ..serializers.goals import GoalSerializer
from ..permissions import IsOwner
from ..filters import GoalFilter


class GoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing financial goals.
    """

    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = GoalFilter
    search_fields = ["name"]
    ordering_fields = ["name", "deadline", "created_at"]
    ordering = ["deadline"]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)
