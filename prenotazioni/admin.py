from django.contrib import admin
from .models import Prenotazione, Disponibilita, Assenza
# Importa TUTTI i tuoi form personalizzati
from .forms import PrenotazioneForm, DisponibilitaForm, AssenzaForm 

class PrenotazioneAdmin(admin.ModelAdmin):
    # Usiamo il form personalizzato per le validazioni
    form = PrenotazioneForm 
    list_display = ('id', 'paziente', 'terapeuta', 'data_ora')
    list_filter = ('terapeuta',)

class DisponibilitaAdmin(admin.ModelAdmin):
    # Colleghiamo il form di validazione
    form = DisponibilitaForm
    # Sostituito 'data' con 'giorno'
    list_display = ('terapeuta', 'giorno', 'ora_inizio', 'ora_fine')
    list_filter = ('terapeuta', 'giorno')

class AssenzaAdmin(admin.ModelAdmin):
    # Colleghiamo il form di validazione
    form = AssenzaForm
    list_display = ('terapeuta', 'data_inizio', 'data_fine')
    list_filter = ('terapeuta',) # Nota la virgola, list_filter richiede una tupla
    
# Registriamo i modelli collegandoli alle nuove classi Admin
admin.site.register(Prenotazione, PrenotazioneAdmin)
admin.site.register(Disponibilita, DisponibilitaAdmin)
admin.site.register(Assenza, AssenzaAdmin)