from django import forms
from prenotazioni.models import Prenotazione, Disponibilita, Assenza
from django.utils import timezone

class PrenotazioneForm(forms.ModelForm):
    data_ora = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M'] 
    )

    class Meta:
        model = Prenotazione
        fields = ['data_ora', 'terapeuta', 'durata_minuti']
        widgets = {
            'terapeuta': forms.Select(),
            'durata_minuti': forms.NumberInput(attrs={'min': 15, 'max': 120, 'step': 15}),
        }

    def clean(self):
        dati_puliti = super().clean()
        data_scelta = dati_puliti.get('data_ora')

        if data_scelta and data_scelta < timezone.now():
            self.add_error('data_ora', "La data e l'ora della prenotazione non possono essere nel passato.")

        if data_scelta and (data_scelta.hour < 8 or data_scelta.hour > 20):
            self.add_error('data_ora', "Le prenotazioni possono essere effettuate solo tra le 08:00 e le 20:00.")
        
        return dati_puliti

class DisponibilitaForm(forms.ModelForm):
    class Meta:
        model = Disponibilita
        fields = ['giorno', 'ora_inizio', 'ora_fine', 'studio']
        widgets = {
            'ora_inizio': forms.TimeInput(attrs={'type': 'time'}),
            'ora_fine': forms.TimeInput(attrs={'type': 'time'}),
        }

    # Questo metodo intercetta il terapeuta che gli abbiamo passato dalla View
    def __init__(self, *args, **kwargs):
        terapeuta = kwargs.pop('terapeuta', None)
        super().__init__(*args, **kwargs)
        if terapeuta:
            # MAGIA: Limitiamo il menu a tendina solo agli studi del medico loggato
            self.fields['studio'].queryset = terapeuta.studi.all()
            self.instance.terapeuta = terapeuta  # Imposta il terapeuta dell'istanza del form

    def clean(self):
        dati_puliti = super().clean()
        ora_inizio = dati_puliti.get('ora_inizio')
        ora_fine = dati_puliti.get('ora_fine')

        if ora_inizio and ora_fine and ora_inizio >= ora_fine:
            self.add_error('ora_fine', "L'ora di fine deve essere successiva all'ora di inizio.")
        return dati_puliti

class AssenzaForm(forms.ModelForm):
    class Meta:
        model = Assenza
        fields = ['data_ora_inizio', 'data_ora_fine', 'motivazione']
        widgets = {
            'data_ora_inizio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'data_ora_fine': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        dati_puliti = super().clean()
        data_ora_inizio = dati_puliti.get('data_ora_inizio')
        data_ora_fine = dati_puliti.get('data_ora_fine')

        if data_ora_inizio and data_ora_fine and data_ora_inizio >= data_ora_fine:
            self.add_error('data_ora_fine', "L'ora di fine deve essere successiva all'ora di inizio.")
        return dati_puliti

    def __init__(self, *args, **kwargs):
        terapeuta = kwargs.pop('terapeuta', None)
        super().__init__(*args, **kwargs)
        if terapeuta:
            self.instance.terapeuta = terapeuta  # Imposta il terapeuta dell'istanza del form