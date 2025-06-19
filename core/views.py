from django.http import JsonResponse
from rest_framework import viewsets
from .models import (
    User, Subject, Inscription, Evaluation,
    Grade, ConsultationResource, AgentInteraction
)
from .serializers import (
    UserSerializer, SubjectSerializer, InscriptionSerializer,
    EvaluationSerializer, GradeSerializer,
    ConsultationResourceSerializer, AgentInteractionSerializer
)


def api_root(request):
    return JsonResponse({
        "message": "¡El asistente académico está activo!",
        "swagger": "/swagger/",
        "admin": "/admin/",
        "api": "/api/"
    })


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
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

