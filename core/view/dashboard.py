from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from core.models import Subject, Evaluation
from django.db.models import Prefetch

@login_required
def dashboard_view(request):
    """
    Muestra únicamente las materias en las que este usuario
    ha sincronizado evaluaciones, junto a sus propias evaluaciones.
    """
    subjects = (
        Subject.objects
               .filter(evaluations__user=request.user)      # solo materias con evals de este usuario
               .distinct()
               .order_by('trimestre')
               .prefetch_related(
                   Prefetch(
                       'evaluations',
                       queryset=Evaluation.objects
                                         .filter(user=request.user)
                                         .order_by('fecha_inicio'),
                       to_attr='user_evals'                   # las guarda en subject.user_evals
                   )
               )
    )

    return render(request, "dashboard.html", {
        'subjects': subjects
    })


def register_view(request):
    return render(request, 'register.html')

def login_view(request):
    next_url = request.GET.get('next', '/dashboard/')
    if request.method == 'POST':
        ci       = request.POST.get('ci')
        password = request.POST.get('password')
        user = authenticate(request, username=ci, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, "Credenciales inválidas")

    return render(request, 'login.html', {
        'next': next_url
    })

def logout_view(request):
    logout(request)
    return redirect('login')
