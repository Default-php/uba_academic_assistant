from rest_framework import serializers
from .models import (
    User, Subject, Inscription, Evaluation,
    Grade, ConsultationResource, AgentInteraction
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class InscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscription
        fields = '__all__'


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'


class ConsultationResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationResource
        fields = '__all__'


class AgentInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentInteraction
        fields = '__all__'
