from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("organizations", views.OrganizationViewSet, basename="organization")
router.register("roles", views.RoleViewSet, basename="role")
router.register("memberships", views.MembershipViewSet, basename="membership")

urlpatterns = [
    path("features/", views.FeatureListView.as_view(), name="feature-list"),
    path("org-users/", views.OrgUserListView.as_view(), name="org-users"),
    path("", include(router.urls)),
]
