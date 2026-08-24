from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q

class Prenotazione(models.Model):
    paziente = models.ForeignKey('utenti.Paziente', on_delete=models.CASCADE, related_name='prenotazioni')
    terapeuta = models.ForeignKey('utenti.Terapeuta', on_delete=models.CASCADE, related_name='prenotazioni')
    
    data_ora = models.DateTimeField() 
    durata_minuti = models.PositiveIntegerField(default=60)
    letta_da_medico = models.BooleanField(default=False)
    
    STATO_CHOICES = [
        ('in_programma', 'In Programma'),
        ('cancellata', 'Cancellata'),
    ]
    stato = models.CharField(max_length=20, choices=STATO_CHOICES, default='in_programma')
    
    def __str__(self):
        return f"Prenotazione {self.id} - Paziente: {self.paziente} | Terapeuta: {self.terapeuta} ({self.data_ora})"

    class Meta:
        verbose_name = "Prenotazione"
        verbose_name_plural = "Prenotazioni"
        ordering = ['data_ora']
        constraints = [
            models.UniqueConstraint(fields=['terapeuta', 'data_ora'], name='unica_seduta_terapeuta')
        ]

    def clean(self):
        data_fine_scelta = self.data_ora + timedelta(minutes=self.durata_minuti)
        
        # 1. Controllo sovrapposizioni per il Terapeuta
        prenotazioni_esistenti = Prenotazione.objects.filter(
            terapeuta=self.terapeuta,
            data_ora__date=self.data_ora.date(),
            stato='in_programma'
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
            data_ora__date=self.data_ora.date(),
            stato='in_programma'
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
        (0, 'Lunedì'), (1, 'Martedì'), (2, 'Mercoledì'),
        (3, 'Giovedì'), (4, 'Venerdì'), (5, 'Sabato'), (6, 'Domenica'),
    ]
    terapeuta = models.ForeignKey('utenti.Terapeuta', on_delete=models.CASCADE, related_name='disponibilita')
    studio = models.ForeignKey('utenti.Studio', on_delete=models.CASCADE, related_name='disponibilita', default=None)
    giorno = models.IntegerField(choices=GIORNI_SETTIMANA)
    ora_inizio = models.TimeField()
    ora_fine = models.TimeField()

    class Meta:
        verbose_name = "Disponibilità"
        verbose_name_plural = "Disponibilità"
        ordering = ['giorno', 'ora_inizio']
        constraints = [
            models.UniqueConstraint(fields=['terapeuta', 'studio', 'giorno', 'ora_inizio', 'ora_fine'], name='unica_disponibilita')
        ]

    def __str__(self):
        return f"{self.terapeuta} - {self.get_giorno_display()}: {self.ora_inizio} - {self.ora_fine}"

    def clean(self):
        if self.ora_inizio and self.ora_fine:
            if self.ora_inizio.minute != 0:
                raise ValidationError({'ora_inizio': "L'orario di inizio deve essere un'ora esatta (es. 09:00, 10:00)."})
            if self.ora_fine.minute != 0:
                raise ValidationError({'ora_fine': "L'orario di fine deve essere un'ora esatta (es. 10:00, 11:00)."})
            if self.ora_inizio >= self.ora_fine:
                raise ValidationError("L'orario di inizio deve essere precedente all'orario di fine.")

            sovrapposizioni = Disponibilita.objects.filter(
                terapeuta=self.terapeuta, giorno=self.giorno
            ).filter(Q(ora_inizio__lt=self.ora_fine) & Q(ora_fine__gt=self.ora_inizio))
            
            if self.pk:
                sovrapposizioni = sovrapposizioni.exclude(pk=self.pk)
            if sovrapposizioni.exists():
                raise ValidationError("Questa fascia oraria si sovrappone a una disponibilità già esistente per questo giorno.")

class Assenza(models.Model):
    terapeuta = models.ForeignKey('utenti.Terapeuta', on_delete=models.CASCADE, related_name='assenze')
    data_inizio = models.DateField(default=None)
    data_fine = models.DateField(default=None)
    motivazione = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Assenza"
        verbose_name_plural = "Assenze"
        ordering = ['data_inizio']

    def clean(self):
        if self.data_inizio and self.data_fine and self.data_inizio > self.data_fine:
            raise ValidationError("La data di fine non può essere precedente alla data di inizio.")
        if not self.data_inizio or not self.data_fine:
            return

        prenotazioni_esistenti = Prenotazione.objects.filter(
            terapeuta=self.terapeuta,
            data_ora__date__gte=self.data_inizio,
            data_ora__date__lte=self.data_fine,
            stato='in_programma'
        )
        if prenotazioni_esistenti.exists():
            p = prenotazioni_esistenti.first()
            raise ValidationError(f"Non puoi segnare un'assenza: hai già una seduta fissata il {p.data_ora.strftime('%d/%m/%Y alle %H:%M')}.")

    def __str__(self):
        return f"Assenza {self.terapeuta}: dal {self.data_inizio.strftime('%d/%m/%Y')} al {self.data_fine.strftime('%d/%m/%Y')}"