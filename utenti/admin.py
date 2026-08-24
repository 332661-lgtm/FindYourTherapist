from django.contrib import admin
from utenti.models import Terapeuta, Paziente, Studio, Specializzazione 
# Register your models here.
from django.contrib import admin
from .models import Terapeuta

@admin.register(Terapeuta)
class TerapeutaAdmin(admin.ModelAdmin):
    # Mostra queste colonne nella tabella
    list_display = ('user', 'prezzo', 'verified')
    # Rende la colonna 'verified' cliccabile direttamente dalla lista!
    list_editable = ('verified',)

admin.site.register(Paziente)
admin.site.register(Studio)
admin.site.register(Specializzazione)
