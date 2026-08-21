from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from core.view.assistant import AssistantAPIView

from .views import (
    AgentInteractionViewSet,
    ConsultationResourceViewSet,
    EvaluationChatView,
    EvaluationViewSet,
    GradeViewSet,
    InscriptionViewSet,
    LogoutView,
    RegisterView,
    SubjectViewSet,
    UserViewSet,
    api_root,
)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"subjects", SubjectViewSet)
router.register(r"inscriptions", InscriptionViewSet)
router.register(r"evaluations", EvaluationViewSet)
router.register(r"grades", GradeViewSet)
router.register(r"resources", ConsultationResourceViewSet)
router.register(r"interactions", AgentInteractionViewSet)


urlpatterns = [
    path("", api_root, name="api-root"),
    path("", include(router.urls)),
    # Endpoints de autenticación JWT
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="token_logout"),
    path("chat/", AssistantAPIView.as_view(), name="api_chat"),
    path("chat/<int:eval_id>/", EvaluationChatView.as_view(), name="evaluation_chat"),
]
