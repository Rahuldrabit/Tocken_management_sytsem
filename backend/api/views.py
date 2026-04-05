import logging

from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, views
from rest_framework.response import Response
from .models import Ticket, TicketComment, KnowledgeBase, Status, Priority
from .serializers import (
    TicketSerializer,
    TicketCommentSerializer,
    KnowledgeBaseSerializer,
    StatusSerializer,
    PrioritySerializer,
    AdminUserSerializer,
)
from .tasks import process_new_ticket_task
from .permissions import (
    IsOwnerOrStaff,
    IsCommentOwnerOrTicketOwnerOrStaff,
    IsAdminOrReadOnly,
    IsCustomerUser,
    IsStaffOnly,
    IsAdminOnly,
)

logger = logging.getLogger(__name__)

class CurrentUserView(views.APIView):
    """Return current authenticated user's profile and role information"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
        })

class AdminDashboardStatsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request):
        total_tickets = Ticket.objects.count()
        # Mock logic to count escalations based on comment drafts needing review
        escalated_tickets = TicketComment.objects.filter(comment_text__icontains="[ESCALATION").count() 
        open_tickets = Ticket.objects.filter(status_id=1).count()
        
        recent_tickets = Ticket.objects.select_related('customer', 'status', 'priority').order_by('-created_at')[:10]
        serializer = TicketSerializer(recent_tickets, many=True)
        
        return Response({
            "metrics": {
                "total_tickets": total_tickets,
                "escalated_tickets": escalated_tickets,
                "open_tickets": open_tickets,
                "resolved_tickets": total_tickets - open_tickets
            },
            "recent_tickets": serializer.data
        })

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related('customer', 'status', 'priority').all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        qs = Ticket.objects.select_related('customer', 'status', 'priority').all()
        if self.request.user.is_staff:
            return qs
        return qs.filter(customer=self.request.user)

    def perform_create(self, serializer):
        ticket = serializer.save(customer=self.request.user)
        try:
            process_new_ticket_task.delay(ticket.id)
        except Exception as exc:
            # Keep ticket creation available even if broker/worker is unavailable.
            logger.warning("Async AI processing unavailable, running inline: %s", exc)
            process_new_ticket_task(ticket.id)

class TicketCommentViewSet(viewsets.ModelViewSet):
    queryset = TicketComment.objects.select_related('user').all()
    serializer_class = TicketCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentOwnerOrTicketOwnerOrStaff]

    def get_queryset(self):
        qs = TicketComment.objects.select_related('user', 'ticket', 'ticket__customer').all()
        if self.request.user.is_staff:
            return qs
        return qs.filter(ticket__customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeBase.objects.all()
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

class PriorityViewSet(viewsets.ModelViewSet):
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


# Role-specific endpoints
class CustomerTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related('customer', 'status', 'priority').all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerUser, IsOwnerOrStaff]

    def get_queryset(self):
        return Ticket.objects.select_related('customer', 'status', 'priority').filter(customer=self.request.user)

    def perform_create(self, serializer):
        ticket = serializer.save(customer=self.request.user)
        try:
            process_new_ticket_task.delay(ticket.id)
        except Exception as exc:
            logger.warning("Async AI processing unavailable, running inline: %s", exc)
            process_new_ticket_task(ticket.id)


class StaffTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related('customer', 'status', 'priority').all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOnly]

    def perform_create(self, serializer):
        ticket = serializer.save(customer=self.request.user)
        try:
            process_new_ticket_task.delay(ticket.id)
        except Exception as exc:
            logger.warning("Async AI processing unavailable, running inline: %s", exc)
            process_new_ticket_task(ticket.id)


class AdminTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related('customer', 'status', 'priority').all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOnly]


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOnly]
