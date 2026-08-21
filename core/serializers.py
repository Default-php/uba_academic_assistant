from rest_framework import serializers

from .models import ConsultationResource, Evaluation, Grade, Inscription, Subject, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["ci", "nombre_completo", "correo", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "ci",
            "nombre_completo",
            "correo",
            "carrera",
            "trimestre",
            "fecha_registro",
            "is_synced",
            "last_synced",
        ]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class InscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscription
        fields = "__all__"


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = "__all__"


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = "__all__"


class ConsultationResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationResource
        fields = "__all__"
