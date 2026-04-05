from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TicketViewSet,
    TicketCommentViewSet,
    KnowledgeBaseViewSet,
    StatusViewSet,
    PriorityViewSet,
    AdminDashboardStatsView,
    CurrentUserView,
    CustomerTicketViewSet,
    StaffTicketViewSet,
    AdminTicketViewSet,
    AdminUserViewSet,
)

router = DefaultRouter()
router.register(r'tickets', TicketViewSet)
router.register(r'comments', TicketCommentViewSet)
router.register(r'kb', KnowledgeBaseViewSet)
router.register(r'statuses', StatusViewSet)
router.register(r'priorities', PriorityViewSet)
router.register(r'customer/tickets', CustomerTicketViewSet, basename='customer-tickets')
router.register(r'staff/tickets', StaffTicketViewSet, basename='staff-tickets')
router.register(r'admin/tickets', AdminTicketViewSet, basename='admin-tickets')
router.register(r'admin/users', AdminUserViewSet, basename='admin-users')

urlpatterns = [
    path('', include(router.urls)),
    path('user/me/', CurrentUserView.as_view(), name='current_user'),
    path('admin-stats/', AdminDashboardStatsView.as_view(), name='admin_stats'),
]
