from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.notifications.models import Notification
from ..serializers.notifications import NotificationSerializer
from ..permissions import IsOwner


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    ordering_fields = ["created_at", "is_read"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """
        Mark a notification as read.
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "marked as read"})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """
        Mark all notifications as read.
        """
        self.get_queryset().update(is_read=True)
        return Response({"status": "all marked as read"})

    @action(detail=False, methods=["get"])
    def unread(self, request):
        """
        Get unread notifications.
        """
        queryset = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
