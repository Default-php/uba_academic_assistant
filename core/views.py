from django.http import JsonResponse

def api_root(request):
    return JsonResponse({"message": "¡El asistente académico está activo!"})

