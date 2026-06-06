from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.rbac.permissions import CanViewAudit

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, CanViewAudit]

    def get_queryset(self):
        org_id = self.request.query_params.get("org_id")
        qs = AuditLog.objects.select_related("user", "organization")
        if org_id:
            qs = qs.filter(
                Q(organization_id=org_id)
                | Q(
                    organization__isnull=True,
                    user__memberships__organization_id=org_id,
                )
            ).distinct()
        return qs[:200]
