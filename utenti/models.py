from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Studio(models.Model):
    indirizzo = models.CharField(max_length=200)
    citta = models.CharField(max_length=100)

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


