from django.shortcuts import render
from core.models import Subject, Evaluation
from django.db.models import Prefetch


def dashboard_view(request):
    subjects = Subject.objects.prefetch_related(
        Prefetch(
            'evaluations',
            queryset=Evaluation.objects.order_by('fecha_inicio')
        )
    ).order_by('trimestre')

    context = {
        "subjects": subjects
    }
    return render(request, "dashboard.html", context)
