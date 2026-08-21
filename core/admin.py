from django.contrib import admin

from .models import ConsultationResource, Evaluation, Grade, Inscription, Subject, User

admin.site.register(User)
admin.site.register(Subject)
admin.site.register(Inscription)
admin.site.register(Evaluation)
admin.site.register(Grade)
admin.site.register(ConsultationResource)
