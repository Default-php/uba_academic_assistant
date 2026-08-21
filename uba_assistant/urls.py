from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

# Swagger (drf-yasg)
from rest_framework import permissions

from core.view.dashboard import dashboard_view, login_view, logout_view, register_view

schema_view = get_schema_view(
    openapi.Info(
        title="UBA Assistant API",
        default_version="v1",
        description="Documentación interactiva del asistente académico",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def index_view(request):
    return JsonResponse(
        {
            "message": "Bienvenido al Asistente Académico UBA",
            "api_base": "/api/",
            "admin": "/admin/",
            "swagger": "/swagger/",
        }
    )


urlpatterns = [
    path("", index_view),
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("register-page/", register_view, name="register"),
    path("login-page/", login_view, name="login"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("logout/", logout_view, name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
