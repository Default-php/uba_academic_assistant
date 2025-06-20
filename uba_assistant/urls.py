from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

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
]


