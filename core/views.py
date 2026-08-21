from django.db.models import Prefetch
from django.http import JsonResponse
from django_q.tasks import async_task
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ConsultationResource, Evaluation, Grade, Inscription, Subject, User
from .serializers import (
    ConsultationResourceSerializer,
    EvaluationSerializer,
    GradeSerializer,
    InscriptionSerializer,
    RegisterSerializer,
    SubjectSerializer,
    UserSerializer,
)


def api_root(request):
    return JsonResponse(
        {
            "message": "¡El asistente académico está activo!",
            "swagger": "/swagger/",
            "admin": "/admin/",
            "api": "/api/",
        }
    )


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Registro de usuario",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["ci", "nombre_completo", "correo", "password"],
            properties={
                "ci": openapi.Schema(type=openapi.TYPE_STRING, description="Cédula del usuario"),
                "nombre_completo": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Nombre completo del usuario"
                ),
                "correo": openapi.Schema(
                    type=openapi.TYPE_STRING, format="email", description="Correo electrónico"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="password",
                    description="Contraseña del usuario",
                ),
            },
        ),
        responses={
            201: openapi.Response("Usuario creado correctamente"),
            400: openapi.Response("Bad Request"),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {"mensaje": "Usuario creado correctamente"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Token inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        # Devuelve los datos del usuario logueado
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="sync")
    def sync(self, request):
        async_task(
            "core.tasks.sync_for_user",
            request.user.pk,
            request.data.get("ci"),
            request.data.get("password"),
        )
        return Response(
            {"detail": "Sincronización en segundo plano iniciada"}, status=status.HTTP_202_ACCEPTED
        )

    @action(detail=False, methods=["get"], url_path="sync-status")
    def sync_status(self, request):
        u = request.user
        return Response(
            {
                "is_synced": u.is_synced,
                "last_synced": u.last_synced.isoformat() if u.last_synced else None,
            }
        )


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.prefetch_related(
        Prefetch(
            "evaluations",  # <- El nombre que definiste en related_name
            queryset=Evaluation.objects.order_by("fecha_inicio"),
        )
    )
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Subject.objects.filter(evaluations__user=self.request.user)
            .distinct()
            .prefetch_related(
                Prefetch(
                    "evaluations",
                    queryset=Evaluation.objects.filter(user=self.request.user).order_by(
                        "fecha_inicio"
                    ),
                    to_attr="user_evals",
                )
            )
        )


class InscriptionViewSet(viewsets.ModelViewSet):
    queryset = Inscription.objects.all()
    serializer_class = InscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Inscription.objects.filter(usuario=self.request.user)


class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Evaluation.objects.filter(user=self.request.user)


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Grade.objects.filter(usuario=self.request.user)


class ConsultationResourceViewSet(viewsets.ModelViewSet):
    queryset = ConsultationResource.objects.all()
    serializer_class = ConsultationResourceSerializer
    permission_classes = [IsAuthenticated]
