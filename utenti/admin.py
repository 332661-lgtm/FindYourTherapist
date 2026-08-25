from django.contrib import admin
from .models import Terapeuta, Paziente, Studio, Specializzazione 

@admin.register(Terapeuta)
class TerapeutaAdmin(admin.ModelAdmin):
    list_display = ('user', 'prezzo', 'verified')
    #Permette di cliccare la spunta blu dalla lista
    list_editable = ('verified',) 
    list_filter = ('verified', 'studi')

@admin.register(Paziente)
class PazienteAdmin(admin.ModelAdmin):
    list_display = ('user', 'CF', 'numero_telefono')
    search_fields = ('user__first_name', 'user__last_name', 'CF')

@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ('citta', 'indirizzo')
    list_filter = ('citta',)

admin.site.register(Specializzazione)