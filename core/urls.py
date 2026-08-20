from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .auth_views import RegisterView, LogoutView
from core.view.dashboard import dashboard_view, register_view, login_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    RegisterView,
    api_root,
    UserViewSet,
    SubjectViewSet,
    InscriptionViewSet,
    EvaluationViewSet,
    GradeViewSet,
    ConsultationResourceViewSet,
)


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'inscriptions', InscriptionViewSet)
router.register(r'evaluations', EvaluationViewSet)
router.register(r'grades', GradeViewSet)
router.register(r'resources', ConsultationResourceViewSet)


urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),

    # Endpoints de autenticación JWT
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='token_logout'),
]