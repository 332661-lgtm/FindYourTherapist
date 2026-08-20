from django.contrib import admin
from utenti.models import Terapeuta, Paziente, Studio, Specializzazione 
# Register your models here.
admin.site.register(Terapeuta)
admin.site.register(Paziente)
admin.site.register(Studio)
admin.site.register(Specializzazione)
