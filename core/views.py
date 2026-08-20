from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.utils.html import strip_tags
from django_q.tasks import async_task
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser  
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    User, Subject, Inscription, Evaluation,
    Grade, ConsultationResource, AgentInteraction
)
from .serializers import (
    UserSerializer, SubjectSerializer, InscriptionSerializer,
    EvaluationSerializer, GradeSerializer,
    ConsultationResourceSerializer, AgentInteractionSerializer,
    RegisterSerializer
)


def api_root(request):
    return JsonResponse({
        "message": "¡El asistente académico está activo!",
        "swagger": "/swagger/",
        "admin": "/admin/",
        "api": "/api/"
    })

class EvaluationChatView(LoginRequiredMixin, TemplateView):
    template_name = 'evaluation_chat.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ev = get_object_or_404(Evaluation, pk=kwargs['eval_id'], user=self.request.user)
        # extrae texto plano de ev.contenido_html
        ctx['plain_text'] = strip_tags(ev.contenido_html)
        ctx['eval'] = ev
        return ctx
    
class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Registro de usuario",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['ci', 'nombre_completo', 'correo', 'password'],
            properties={
                'ci': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Cédula del usuario"
                ),
                'nombre_completo': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Nombre completo del usuario"
                ),
                'correo': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="email",
                    description="Correo electrónico"
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="password",
                    description="Contraseña del usuario"
                )
            }
        ),
        responses={
            201: openapi.Response("Usuario creado correctamente"),
            400: openapi.Response("Bad Request")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"mensaje": "Usuario creado correctamente"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        # Devuelve los datos del usuario logueado
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='sync')
    def sync(self, request):
        async_task(
            'core.tasks.sync_for_user',
            request.user.pk,
            request.data.get('ci'),
            request.data.get('password')
        )
        return Response(
            {'detail': 'Sincronización en segundo plano iniciada'},
            status=status.HTTP_202_ACCEPTED
        )

    @action(detail=False, methods=['get'], url_path='sync-status')
    def sync_status(self, request):
        u = request.user
        return Response({
            'is_synced':   u.is_synced,
            'last_synced': u.last_synced.isoformat() if u.last_synced else None
        })


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.prefetch_related(
        Prefetch(
            'evaluations',  # <- El nombre que definiste en related_name
            queryset=Evaluation.objects.order_by('fecha_inicio')
        )
    )
    serializer_class = SubjectSerializer

class InscriptionViewSet(viewsets.ModelViewSet):
    queryset = Inscription.objects.all()
    serializer_class = InscriptionSerializer


class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class ConsultationResourceViewSet(viewsets.ModelViewSet):
    queryset = ConsultationResource.objects.all()
    serializer_class = ConsultationResourceSerializer


class AgentInteractionViewSet(viewsets.ModelViewSet):
    queryset = AgentInteraction.objects.all()
    serializer_class = AgentInteractionSerializer

