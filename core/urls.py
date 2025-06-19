from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'subjects', views.SubjectViewSet)
router.register(r'inscriptions', views.InscriptionViewSet)
router.register(r'evaluations', views.EvaluationViewSet)
router.register(r'grades', views.GradeViewSet)
router.register(r'resources', views.ConsultationResourceViewSet)
router.register(r'interactions', views.AgentInteractionViewSet)

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('', include(router.urls)),  # 👈 Incluye rutas generadas automáticamente
]
