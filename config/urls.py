from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.rbac.urls")),
    path("api/", include("apps.audit.urls")),
    path("", include("apps.accounts.web_urls")),
]
