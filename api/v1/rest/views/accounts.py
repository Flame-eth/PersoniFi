from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import Account
from ..serializers.accounts import AccountSerializer
from ..permissions import IsOwner
from ..filters import AccountFilter


class AccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user accounts.
    """

    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = AccountFilter
    search_fields = ["name", "institution"]
    ordering_fields = ["name", "balance", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
