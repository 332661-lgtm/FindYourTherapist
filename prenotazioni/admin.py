from django.contrib import admin
from .models import Prenotazione, Disponibilita, Assenza
from utenti.models import RelazioneTerapeutica, CartellaFile, Documento # I nuovi modelli!
from .forms import PrenotazioneForm, DisponibilitaForm, AssenzaForm 

class PrenotazioneAdmin(admin.ModelAdmin):
    form = PrenotazioneForm 
    list_display = ('id', 'paziente', 'terapeuta', 'data_ora', 'stato')
    list_filter = ('terapeuta', 'stato')

class DisponibilitaAdmin(admin.ModelAdmin):
    form = DisponibilitaForm
    list_display = ('terapeuta', 'giorno', 'ora_inizio', 'ora_fine')
    list_filter = ('terapeuta', 'giorno')

class AssenzaAdmin(admin.ModelAdmin):
    form = AssenzaForm
    list_display = ('terapeuta', 'data_inizio', 'data_fine')
    list_filter = ('terapeuta',) 
    
# Registrazione modelli vecchi
admin.site.register(Prenotazione, PrenotazioneAdmin)
admin.site.register(Disponibilita, DisponibilitaAdmin)
admin.site.register(Assenza, AssenzaAdmin)

@admin.register(RelazioneTerapeutica)
class RelazioneTerapeuticaAdmin(admin.ModelAdmin):
    list_display = ('terapeuta', 'paziente', 'paziente_puo_caricare_file')
    list_editable = ('paziente_puo_caricare_file',)

@admin.register(CartellaFile)
class CartellaFileAdmin(admin.ModelAdmin):
    list_display = ('nome', 'relazione', 'is_condivisa', 'data_creazione')
    list_filter = ('is_condivisa',)

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('nome_originale', 'cartella', 'caricato_da', 'data_caricamento')