from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """Allow read for authenticated users; writes are admin/staff only."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_staff)


class IsOwnerOrStaff(BasePermission):
    """Ticket object access for owner or staff users."""

    def has_object_permission(self, request, view, obj):
        return bool(request.user and (request.user.is_staff or obj.customer_id == request.user.id))


class IsCommentOwnerOrTicketOwnerOrStaff(BasePermission):
    """Comment object access for comment author, ticket owner, or staff users."""

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and (
                request.user.is_staff
                or obj.user_id == request.user.id
                or obj.ticket.customer_id == request.user.id
            )
        )


class IsCustomerUser(BasePermission):
    """Customer role: authenticated and not staff/admin."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and not request.user.is_staff)


class IsStaffOnly(BasePermission):
    """Staff role only, excluding superusers to keep admin separate."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and not request.user.is_superuser
        )


class IsAdminOnly(BasePermission):
    """Admin role: superuser only."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
