from django import forms
from django.contrib.auth.models import User
from .models import Paziente, Terapeuta, Studio, Specializzazione

class RegistrazionePazienteForm(forms.ModelForm):
    numero_telefono = forms.CharField(max_length=15, required=True, label="Numero di telefono")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Conferma Password", required=True)
    
    data_nascita = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    indirizzo = forms.CharField(max_length=200, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'numero_telefono', 'password', 'password_confirm', 'data_nascita', 'indirizzo']
        
        widgets = {
            'password': forms.PasswordInput(),
        }
        labels = {
            'first_name': 'Nome',
            'last_name': 'Cognome',
            'email': 'Email',
        }
        help_texts = {
            'username': None,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    def clean(self):
        dati_puliti = super().clean()
        password = dati_puliti.get('password')
        password_confirm = dati_puliti.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Le password non coincidono.')

        return dati_puliti

class RegistrazioneTerapeutaForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    conferma_password = forms.CharField(widget=forms.PasswordInput, label="Conferma Password")
    numero_telefono = forms.CharField(max_length=15, required=False, label="Numero di Telefono (Opzionale)")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Cognome'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        conferma_password = cleaned_data.get("conferma_password")

        if password and conferma_password and password != conferma_password:
            self.add_error('conferma_password', "Le password non coincidono.")
        return cleaned_data

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Cognome',
            'email': 'Email',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

class PazienteUpdateForm(forms.ModelForm):
    class Meta:
        model = Paziente
        fields = ['numero_telefono', 'data_nascita', 'indirizzo']
        widgets = {
            'data_nascita': forms.DateInput(attrs={'type': 'date'})
        }
        labels = {
            'numero_telefono': 'Numero di telefono',
            'data_nascita': 'Data di nascita',
            'indirizzo': 'Indirizzo completo'
        }

class TerapeutaUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Terapeuta
        fields = ['numero_telefono', 'prezzo', 'descrizione', 'studi', 'specializzazioni']
        labels = {
            'numero_telefono': 'Numero di telefono',
            'prezzo': 'Prezzo a seduta (€)',
            'descrizione': 'Descrizione / Biografia',
            'studi': 'I tuoi studi attuali',
            'specializzazioni': 'Le tue specializzazioni'
        }
        widgets = {
            # Blocchiamo il resize via CSS in linea e mettiamo il maxlength a 500
            'descrizione': forms.Textarea(attrs={'rows': 4, 'maxlength': '500', 'style': 'resize: none;'}),
            'specializzazioni': forms.CheckboxSelectMultiple(),
            'studi': forms.CheckboxSelectMultiple(),
        }