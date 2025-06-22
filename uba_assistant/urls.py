from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from core.view.dashboard import dashboard_view
from django.conf import settings
from django.conf.urls.static import static

# Swagger (drf-yasg)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="UBA Assistant API",
      default_version='v1',
      description="Documentación interactiva del asistente académico",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

def index_view(request):
    return JsonResponse({
        "message": "Bienvenido al Asistente Académico UBA",
        "api_base": "/api/",
        "admin": "/admin/",
        "swagger": "/swagger/"
    })

urlpatterns = [
    path('', index_view),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("dashboard/", dashboard_view, name="dashboard")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

