from django.db import models
from utenti.models import Paziente, Terapeuta

class Prenotazione(models.Model):
    # L'ID auto-incrementante viene generato automaticamente da Django, non serve scriverlo.
    paziente = models.ForeignKey('utenti.Paziente', on_delete=models.CASCADE, related_name='prenotazioni')
    terapeuta = models.ForeignKey('utenti.Terapeuta', on_delete=models.CASCADE, related_name='prenotazioni')
    
    # Rimosso unique=True per permettere a terapeuti diversi di lavorare allo stesso orario
    data_ora = models.DateTimeField() 
    durata_minuti = models.PositiveIntegerField(default=60)
    
    stato = models.CharField(max_length=20, default="Confermata")

    def __str__(self):
        return f"Prenotazione {self.id} - Paziente: {self.paziente} | Terapeuta: {self.terapeuta} ({self.data_ora})"

    class Meta:
        verbose_name = "Prenotazione"
        verbose_name_plural = "Prenotazioni"
        ordering = ['data_ora']
        # Questo vincolo impedisce le sovrapposizioni per lo stesso terapeuta
        constraints = [
            models.UniqueConstraint(fields=['terapeuta', 'data_ora'], name='unica_seduta_terapeuta')
        ]

# prenotazioni/models.py

class Disponibilita(models.Model):
    GIORNI_SETTIMANA = [
        (0, 'Lunedì'),
        (1, 'Martedì'),
        (2, 'Mercoledì'),
        (3, 'Giovedì'),
        (4, 'Venerdì'),
        (5, 'Sabato'),
        (6, 'Domenica'),
    ]

    # Collegamento al terapeuta (usa la stringa 'utenti.Terapeuta' per evitare import circolari)
    terapeuta = models.ForeignKey('utenti.Terapeuta', on_delete=models.CASCADE, related_name='disponibilita')
    giorno = models.IntegerField(choices=GIORNI_SETTIMANA)
    ora_inizio = models.TimeField()
    ora_fine = models.TimeField()

    class Meta:
        verbose_name = "Disponibilità"
        verbose_name_plural = "Disponibilità"
        ordering = ['giorno', 'ora_inizio']
        # Evita che il terapeuta inserisca due volte lo stesso orario nello stesso giorno
        constraints = [
            models.UniqueConstraint(fields=['terapeuta', 'giorno', 'ora_inizio', 'ora_fine'], name='unica_disponibilita')
        ]

    def __str__(self):
        return f"{self.terapeuta} - {self.get_giorno_display()}: {self.ora_inizio} - {self.ora_fine}"

class Assenza(models.Model):
    terapeuta = models.ForeignKey('utenti.Terapeuta', on_delete=models.CASCADE, related_name='assenze')
    data_ora_inizio = models.DateTimeField()
    data_ora_fine = models.DateTimeField()
    
    # Campo opzionale per ricordarsi il motivo (es. "Ferie Estive", "Malattia", "Corso di aggiornamento")
    motivazione = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Assenza"
        verbose_name_plural = "Assenze"
        ordering = ['data_ora_inizio']

    def __str__(self):
        return f"Assenza {self.terapeuta}: dal {self.data_ora_inizio.strftime('%d/%m/%Y %H:%M')} al {self.data_ora_fine.strftime('%d/%m/%Y %H:%M')}"