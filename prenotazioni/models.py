from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError
from utenti.models import Paziente, Terapeuta
from django.core.exceptions import ValidationError
from django.db.models import Q

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

    def clean(self):
        # 1. Controllo sovrapposizioni per il Terapeuta
        data_fine_scelta = self.data_ora + timedelta(minutes=self.durata_minuti)
        prenotazioni_esistenti = Prenotazione.objects.filter(
            terapeuta=self.terapeuta,
            data_ora__date=self.data_ora.date()
        )
        if self.pk:
            prenotazioni_esistenti = prenotazioni_esistenti.exclude(pk=self.pk)

        for p in prenotazioni_esistenti:
            p_inizio = p.data_ora
            p_fine = p_inizio + timedelta(minutes=p.durata_minuti)
            if self.data_ora < p_fine and data_fine_scelta > p_inizio:
                raise ValidationError("Il terapeuta ha già una seduta in questo orario.")

        # 2. Controllo sovrapposizioni per il Paziente
        prenotazioni_paziente = Prenotazione.objects.filter(
            paziente=self.paziente,
            data_ora__date=self.data_ora.date()
        )
        if self.pk:
            prenotazioni_paziente = prenotazioni_paziente.exclude(pk=self.pk)
            
        for p in prenotazioni_paziente:
            p_inizio = p.data_ora
            p_fine = p_inizio + timedelta(minutes=p.durata_minuti)
            if self.data_ora < p_fine and data_fine_scelta > p_inizio:
                raise ValidationError("Hai già prenotato una seduta in questo orario.")

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
    studio = models.ForeignKey('utenti.Studio', on_delete=models.CASCADE, related_name='disponibilita', default=None)
    giorno = models.IntegerField(choices=GIORNI_SETTIMANA)
    ora_inizio = models.TimeField()
    ora_fine = models.TimeField()

    class Meta:
        verbose_name = "Disponibilità"
        verbose_name_plural = "Disponibilità"
        ordering = ['giorno', 'ora_inizio']
        # Evita che il terapeuta inserisca due volte lo stesso orario nello stesso giorno
        constraints = [
            models.UniqueConstraint(fields=['terapeuta', 'studio', 'giorno', 'ora_inizio', 'ora_fine'], name='unica_disponibilita')
        ]

    def __str__(self):
        return f"{self.terapeuta} - {self.get_giorno_display()}: {self.ora_inizio} - {self.ora_fine}"

    def clean(self):
        # Eseguiamo i controlli matematici SOLO se il Form non li ha cancellati!
        if self.ora_inizio and self.ora_fine:
            # 1. Controllo base: l'ora di inizio deve precedere l'ora di fine
            if self.ora_inizio >= self.ora_fine:
                raise ValidationError("L'orario di inizio deve essere precedente all'orario di fine.")

            # 2. Controllo sovrapposizioni
            sovrapposizioni = Disponibilita.objects.filter(
                terapeuta=self.terapeuta,
                giorno=self.giorno
            ).filter(
                Q(ora_inizio__lt=self.ora_fine) & Q(ora_fine__gt=self.ora_inizio)
            )

            # Se stiamo modificando un record esistente, lo escludiamo dalla ricerca
            if self.pk:
                sovrapposizioni = sovrapposizioni.exclude(pk=self.pk)

            if sovrapposizioni.exists():
                raise ValidationError("Questa fascia oraria si sovrappone a una disponibilità già esistente per questo giorno.")

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

    def clean(self):
        if self.data_ora_inizio and self.data_ora_fine and self.data_ora_inizio >= self.data_ora_fine:
            raise ValidationError("L'ora di fine deve essere successiva all'ora di inizio.")

        # Controllo se l'assenza va a coprire una prenotazione già esistente
        prenotazioni_esistenti = Prenotazione.objects.filter(
            terapeuta=self.terapeuta,
            data_ora__date__gte=self.data_ora_inizio.date(),
            data_ora__date__lte=self.data_ora_fine.date()
        )
        for p in prenotazioni_esistenti:
            p_inizio = p.data_ora
            p_fine = p_inizio + timedelta(minutes=p.durata_minuti)
            if p_inizio < self.data_ora_fine and p_fine > self.data_ora_inizio:
                raise ValidationError(f"Non puoi segnare un'assenza in questo orario: hai già una seduta fissata il {p_inizio.strftime('%d/%m/%Y alle %H:%M')}.")

    def __str__(self):
        return f"Assenza {self.terapeuta}: dal {self.data_ora_inizio.strftime('%d/%m/%Y %H:%M')} al {self.data_ora_fine.strftime('%d/%m/%Y %H:%M')}"