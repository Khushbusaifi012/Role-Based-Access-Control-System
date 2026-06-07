from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.audit.utils import log_audit
from apps.rbac.models import Membership, Organization

from .models import User
from .serializers import UserSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def api_login(request):
    email = (request.data.get("email") or "").strip().lower()
    password = (request.data.get("password") or "").strip()
    user = authenticate(request, username=email, password=password)
    if user is None:
        log_audit(request, action="LOGIN_FAILED", details={"email": email})
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    login(request, user)
    log_audit(request, action="LOGIN", user=user)
    return Response({"user": UserSerializer(user).data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_logout(request):
    log_audit(request, action="LOGOUT", user=request.user)
    logout(request)
    return Response({"message": "Logged out"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_me(request):
    org_id = request.GET.get("org_id")
    data = UserSerializer(request.user).data
    if org_id:
        membership = request.user.get_org_membership(org_id)
        if membership:
            data["role"] = membership.role.name
            data["permissions"] = membership.role.get_enabled_features()
    return Response(data)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    error = None
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        password = (request.POST.get("password") or "").strip()
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            log_audit(request, action="LOGIN", user=user)
            messages.success(request, "Logged in successfully!")
            return redirect("dashboard")
        log_audit(request, action="LOGIN_FAILED", details={"email": email})
        error = "Invalid email or password"
    return render(request, "login.html", {"error": error})


def logout_view(request):
    was_authenticated = request.user.is_authenticated
    if was_authenticated:
        log_audit(request, action="LOGOUT", user=request.user)
    logout(request)
    if was_authenticated:
        messages.success(request, "Logged out successfully!")
    return redirect("login")


@login_required
def dashboard_view(request):
    orgs = Organization.objects.filter(memberships__user=request.user, memberships__is_active=True).distinct()
    org_id = request.GET.get("org") or (orgs.first().id if orgs.exists() else None)
    membership = request.user.get_org_membership(org_id) if org_id else None
    current_org = Organization.objects.filter(id=org_id).first() if org_id else None
    return render(
        request,
        "dashboard.html",
        {
            "organizations": orgs,
            "current_org_id": int(org_id) if org_id else None,
            "current_org_name": current_org.name if current_org else None,
            "membership": membership,
            "permissions": membership.role.get_enabled_features() if membership else [],
            "page_title": "Dashboard",
        },
    )


@login_required
def roles_page(request):
    org_id = request.GET.get("org")
    orgs = Organization.objects.filter(memberships__user=request.user, memberships__is_active=True).distinct()
    if not org_id and orgs.exists():
        org_id = orgs.first().id
    membership = request.user.get_org_membership(org_id) if org_id else None
    can_manage = membership and membership.role.has_feature("roles.manage") if membership else False
    return render(
        request,
        "roles.html",
        {
            "organizations": orgs,
            "current_org_id": int(org_id) if org_id else None,
            "can_manage": can_manage,
        },
    )


@login_required
def audit_page(request):
    org_id = request.GET.get("org")
    orgs = Organization.objects.filter(memberships__user=request.user, memberships__is_active=True).distinct()
    if not org_id and orgs.exists():
        org_id = orgs.first().id
    membership = request.user.get_org_membership(org_id) if org_id else None
    can_view = membership and membership.role.has_feature("audit.view") if membership else False
    return render(
        request,
        "audit.html",
        {
            "organizations": orgs,
            "current_org_id": int(org_id) if org_id else None,
            "can_view": can_view,
        },
    )
