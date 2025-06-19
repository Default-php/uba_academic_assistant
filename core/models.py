from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class User(models.Model):
    """Estudiantes registrados en la app."""
    id = models.AutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=100)
    ci = models.CharField(max_length=15, unique=True)
    correo = models.EmailField(unique=True)
    clave_encriptada = models.CharField(max_length=255)
    carrera = models.CharField(max_length=100, null=True, blank=True)
    trimestre = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        null=True,
        blank=True)    
    fecha_registro = models.DateTimeField(auto_now_add=True)
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
    creditos = models.PositiveSmallIntegerField()
    docente_nombre = models.CharField(max_length=100)  # solo se guarda el nombre

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
    """Evaluaciones dentro de cada materia."""
    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=[('examen', 'Examen'), ('práctica', 'Práctica'), ('trabajo', 'Trabajo'), ('otro', 'Otro')])
    fecha = models.DateField()
    peso = models.DecimalField(max_digits=5, decimal_places=2)  # en porcentaje
    instrucciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.subject})"


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

