from django.shortcuts import render
from django.http import JsonResponse
from core.models import Subject, Evaluation

def dashboard_view(request):
    subjects = Subject.objects.all().order_by('trimestre')
    evaluations = Evaluation.objects.all().order_by('fecha_inicio')
    return render(request, "dashboard.html", {
        "subjects": subjects,
        "evaluations": evaluations,
    })
