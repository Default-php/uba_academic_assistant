from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, ci, nombre_completo, correo, password=None, **extra_fields):
        if not ci:
            raise ValueError('El usuario debe tener una cédula')
        if not correo:
            raise ValueError('El usuario debe tener un correo')

        email = self.normalize_email(correo)
        user = self.model(ci=ci, nombre_completo=nombre_completo, correo=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, ci, nombre_completo, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(ci, nombre_completo, correo, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ci = models.CharField(max_length=15, unique=True)
    nombre_completo = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    carrera = models.CharField(max_length=100, null=True, blank=True)
    trimestre = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        null=True,
        blank=True
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)

    # ─── Campos para sincronización de evaluaciones ───
    is_synced   = models.BooleanField(
        default=False,
        help_text="True si ya ejecutó el scraping de evaluaciones"
    )
    last_synced = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha/hora de la última sincronización"
    )

    objects = CustomUserManager()

    USERNAME_FIELD  = 'ci'
    REQUIRED_FIELDS = ['nombre_completo', 'correo']

    def __str__(self):
        return self.nombre_completo


class Subject(models.Model):
    """Materias disponibles en el campus virtual."""
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    trimestre = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        null=True,
        blank=True)
    creditos = models.PositiveSmallIntegerField(null= True, blank= True)
    profesor = models.CharField(max_length=100, null= True, blank= True)  # solo se guarda el nombre

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Inscription(models.Model):
    """Relación entre usuarios y materias por trimestre."""
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    trimestre = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        null=True,
        blank=True)    
    año_academico = models.CharField(max_length=9)  # Ej: "2024-2025"
    seccion = models.CharField(max_length=5, null=True, blank=True)
    estado = models.CharField(max_length=10, choices=[('inscrita', 'Inscrita'), ('retirada', 'Retirada')], default='inscrita')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} → {self.subject}"


class Evaluation(models.Model):
    # QUE LIGA CADA EVALUACIÓN A UN USUARIO
    user       = models.ForeignKey(
                   settings.AUTH_USER_MODEL,
                   on_delete=models.CASCADE,
                   related_name='evaluations'
                 )

    subject    = models.ForeignKey(
                   Subject,
                   on_delete=models.CASCADE,
                   related_name='evaluations'
                 )
    moodle_id  = models.CharField(max_length=20, unique=True)
    titulo     = models.TextField()
    url        = models.URLField()
    numero     = models.CharField(max_length=50, null=True, blank=True)
    unidad     = models.CharField(max_length=50, null=True, blank=True)
    tipo       = models.CharField(max_length=100, null=True, blank=True)
    seccion    = models.CharField(max_length=50, null=True, blank=True)
    profesor   = models.CharField(max_length=100, null=True, blank=True)
    porcentaje = models.CharField(max_length=10, null=True, blank=True)
    contenido_html = models.TextField(blank=True, null=True)
    fecha_inicio   = models.CharField(max_length=100, null=True, blank=True)
    fecha_cierre   = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        # Mostramos el título y materia
        return f"{self.titulo} ({self.subject.nombre})"


class Grade(models.Model):
    """Nota que el usuario obtuvo en una evaluación."""
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    evaluacion = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    calificacion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.usuario} → {self.evaluacion}: {self.calificacion}"


class ConsultationResource(models.Model):
    """Recursos asignados en las materias (archivos, enlaces, etc.)."""
    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=[('apunte', 'Apunte'), ('libro', 'Libro'), ('video', 'Video'), ('link', 'Link')])
    titulo = models.CharField(max_length=150)
    url = models.URLField(max_length=255, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.titulo} ({self.tipo})"


class AgentInteraction(models.Model):
    """Historial de preguntas y respuestas entre el usuario y el asistente."""
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    pregunta = models.TextField()
    respuesta_generada = models.TextField()
    fecha_hora = models.DateTimeField(auto_now_add=True)
    intencion_detectada = models.CharField(max_length=100, null=True, blank=True)
    confianza = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)  # Ej: 0.85

    def __str__(self):
        return f"{self.usuario} → {self.intencion_detectada or 'Pregunta'}"

