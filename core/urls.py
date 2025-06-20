from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .auth_views import RegisterView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
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
    path('', include(router.urls)),
    
    path('register/', RegisterView.as_view(), name='user-register'),

    # Endpoints de autenticación JWT
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
