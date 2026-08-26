from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Studio(models.Model):
    indirizzo = models.CharField(max_length=200)
    citta = models.CharField(max_length=100)
    foto_studio = models.ImageField(upload_to='foto_studi/', blank=True, null=True)

    def __str__(self):
        return f"{self.indirizzo} - {self.citta}"

    class Meta:
        verbose_name = "Studio"
        verbose_name_plural = "Studi"
        ordering = ['id']

class Specializzazione(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Specializzazione"
        verbose_name_plural = "Specializzazioni"
        ordering = ['id']

class Paziente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    data_nascita = models.DateField(blank=True, null=True)
    numero_telefono = models.CharField(max_length=15, blank=True, null=True)
    indirizzo = models.CharField(max_length=200, blank=True, null=True)
    CF = models.CharField(max_length=16, blank=True, null=True)  # Codice Fiscale
    

    def __str__(self):
        # I nomi e cognomi ora li peschiamo dal modello User di Django
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        verbose_name = "Paziente"
        verbose_name_plural = "Pazienti"
        ordering = ['id']

    # IL BLOCCO DI SICUREZZA PER IL PAZIENTE
    def clean(self):
        # Controlla se a questo utente è già associato un profilo Terapeuta
        if hasattr(self, 'user') and hasattr(self.user, 'terapeuta'):
            raise ValidationError("Sicurezza: Questo utente è già registrato come Terapeuta. Non può avere anche un profilo Paziente.")

class Terapeuta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    numero_telefono = models.CharField(max_length=15, blank=True, null=True)
    # Aggiungiamo la relazione con lo Studio (Un terapeuta lavora in uno o più studi)
    studi = models.ManyToManyField(Studio, related_name='terapeuti', blank=True)
    prezzo = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    descrizione = models.TextField(blank=True, null=True)
    specializzazioni = models.ManyToManyField(Specializzazione, related_name='terapeuti', blank=True)
    pec = models.EmailField(max_length=254, blank=True, null=True)  # PEC del terapeuta
    verified = models.BooleanField(default=False)  # Campo per indicare se il terapeuta è verificato
    link_ordine = models.URLField(max_length=200, blank=True, null=True)  # Link all'ordine degli psicologi
    foto_profilo = models.ImageField(upload_to='foto_profili/terapeuti/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        verbose_name = "Terapeuta"
        verbose_name_plural = "Terapeuti"
        ordering = ['id']

    # IL BLOCCO DI SICUREZZA PER IL TERAPEUTA
    def clean(self):
        # Controlla se a questo utente è già associato un profilo Paziente
        if hasattr(self, 'user') and hasattr(self.user, 'paziente'):
            raise ValidationError("Sicurezza: Questo utente è già registrato come Paziente. Non può avere anche un profilo Terapeuta.")

# 1. IL LEGAME TERAPEUTA-PAZIENTE (Per salvare le impostazioni, come lo switch!)
class RelazioneTerapeutica(models.Model):
    terapeuta = models.ForeignKey(Terapeuta, on_delete=models.CASCADE)
    paziente = models.ForeignKey(Paziente, on_delete=models.CASCADE)
    
    # Questo è il toggle switch della cartella condivisa!
    paziente_puo_caricare_file = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('terapeuta', 'paziente')

# 2. IL SISTEMA A CARTELLE (Supporta sottocartelle infinite)
class CartellaFile(models.Model):
    nome = models.CharField(max_length=100)
    relazione = models.ForeignKey(RelazioneTerapeutica, on_delete=models.CASCADE, related_name="cartelle")
    
    # Questo campo permette a una cartella di stare dentro un'altra cartella
    cartella_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="sottocartelle")
    
    # True = Cartella Condivisa, False = Cartella Paziente (Privata del medico)
    is_condivisa = models.BooleanField(default=False)
    data_creazione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({'Condivisa' if self.is_condivisa else 'Privata'})"

# 3. I DOCUMENTI FISICI
class Documento(models.Model):
    cartella = models.ForeignKey(CartellaFile, on_delete=models.CASCADE, related_name="documenti")
    
    # Il file vero e proprio (Django lo salverà nella cartella media)
    file = models.FileField(upload_to='documenti_clinici/')
    nome_originale = models.CharField(max_length=255)
    
    # Serve per il "pallino": sappiamo se è stato caricato dall'Utente-Paziente o dall'Utente-Medico
    caricato_da = models.ForeignKey(User, on_delete=models.CASCADE)
    data_caricamento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_originale