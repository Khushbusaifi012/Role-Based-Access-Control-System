def get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_audit(
    request,
    action,
    user=None,
    organization=None,
    resource_type="",
    resource_id=None,
    details=None,
):
    from .models import AuditLog

    if user and organization is None and action in ("LOGIN", "LOGOUT"):
        membership = user.memberships.filter(is_active=True).select_related("organization").first()
        if membership:
            organization = membership.organization

    AuditLog.objects.create(
        user=user or getattr(request, "user", None) if getattr(request, "user", None) and request.user.is_authenticated else None,
        organization=organization,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:300] if request else "",
    )
