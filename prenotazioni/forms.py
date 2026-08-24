from django import forms
from django.core.exceptions import ValidationError
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

        return dati_puliti

class DisponibilitaForm(forms.ModelForm):
    class Meta:
        model = Disponibilita
        fields = ['giorno', 'ora_inizio', 'ora_fine', 'studio']
        widgets = {
            'ora_inizio': forms.TimeInput(attrs={'type': 'time'}),
            'ora_fine': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        terapeuta = kwargs.pop('terapeuta', None)
        super().__init__(*args, **kwargs)
        if terapeuta:
            self.fields['studio'].queryset = terapeuta.studi.all()
            self.instance.terapeuta = terapeuta

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
        fields = ['data_inizio', 'data_fine', 'motivazione']
        widgets = {
            'data_inizio': forms.DateInput(attrs={'type': 'date'}),
            'data_fine': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        dati_puliti = super().clean()
        data_inizio = dati_puliti.get('data_inizio')
        data_fine = dati_puliti.get('data_fine')

        if data_inizio and data_fine and data_inizio >= data_fine:
            self.add_error('data_fine', "La data di fine deve essere successiva alla data di inizio.")
        return dati_puliti

    def __init__(self, *args, **kwargs):
        terapeuta = kwargs.pop('terapeuta', None)
        super().__init__(*args, **kwargs)
        if terapeuta:
            self.instance.terapeuta = terapeuta

# IL FORM PER LA MODIFICA SEMPLICE DA PARTE DEL MEDICO
class ModificaPrenotazioneForm(forms.ModelForm):
    class Meta:
        model = Prenotazione
        fields = ['data_ora']
        widgets = {
            'data_ora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_data_ora(self):
        data_ora = self.cleaned_data.get('data_ora')
        if data_ora.minute != 0:
            raise ValidationError("I colloqui possono essere fissati solo a ore intere (es. 15:00, 16:00).")
        
        sovrapposizioni = Prenotazione.objects.filter(
            terapeuta=self.instance.terapeuta,
            data_ora=data_ora,
            stato='in_programma'
        ).exclude(pk=self.instance.pk)
        
        if sovrapposizioni.exists():
            raise ValidationError("Attenzione: hai già un altro colloquio in programma in questo orario.")
        
        return data_ora