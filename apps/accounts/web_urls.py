from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard_view, name="dashboard"),
    path("roles/", views.roles_page, name="roles"),
    path("audit/", views.audit_page, name="audit"),
]
