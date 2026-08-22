from django.contrib import messages

from django.shortcuts import redirect, render
from .forms import AssenzaForm, DisponibilitaForm, PrenotazioneForm
from django.views import View
from .models import Assenza, Prenotazione, Disponibilita, Terapeuta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

class AggiungiPrenotazioneView(LoginRequiredMixin, View):
    def get(self, request):
        if not hasattr(request.user, 'paziente'):
            messages.error(request, "Accesso negato: non possiedi un profilo paziente.")
            return redirect('home')
        form = PrenotazioneForm()
        return render(request, 'prenotazioni/prenotazione.html', {'form': form})

    def post(self, request):
        if not hasattr(request.user, 'paziente'):
            messages.error(request, "Accesso negato: non possiedi un profilo paziente.")
            return redirect('home')
        form = PrenotazioneForm(request.POST)

        if form.is_valid():
            # 1. Metti in pausa il salvataggio per creare l'oggetto "prenotazione"
            #commit = false significa che non salverà ancora nel database 
            prenotazione = form.save(commit=False)
            # 2. Inserisci il dato mancante (l'auto-compilazione)
            prenotazione.paziente = request.user.paziente  
            # 3. Salva definitivamente nel database
            prenotazione.save()
            return redirect('prenotazioni:prenotazione')  # Redirect to a success page or the same page
        return render(request, 'prenotazioni/prenotazione.html', {'form': form})
    
class AggiungiDisponibilitaView(LoginRequiredMixin, View):
    def get(self, request):
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Accesso negato: non possiedi un profilo terapeuta.")
            return redirect('home')
        # INIETTIAMO IL TERAPEUTA NEL FORM!
        form = DisponibilitaForm(terapeuta=request.user.terapeuta)
        return render(request, 'prenotazioni/disponibilita.html', {'form': form}) 

    def post(self, request):
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Accesso negato: non possiedi un profilo terapeuta.")
            return redirect('home')
        # INIETTIAMO IL TERAPEUTA NEL FORM ANCHE QUI!
        form = DisponibilitaForm(request.POST, terapeuta=request.user.terapeuta)
        if form.is_valid():
            form.save()  # Salva la disponibilità nel database
            return redirect('prenotazioni:disponibilita')
        return render(request, 'prenotazioni/disponibilita.html', {'form': form})

class AggiungiAssenzaView(LoginRequiredMixin, View):
    def get(self, request):
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Accesso negato: non possiedi un profilo terapeuta.")
            return redirect('home')
        form = AssenzaForm()
        return render(request, 'prenotazioni/assenza.html', {'form': form}) 

    def post(self, request):
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Accesso negato: non possiedi un profilo terapeuta.")
            return redirect('home')
        form = AssenzaForm(request.POST, terapeuta=request.user.terapeuta)
        if form.is_valid():
            form.save()
            return redirect('prenotazioni:assenza')  # Redirect to a success page or the same page
        return render(request, 'prenotazioni/assenza.html', {'form': form})

class VisualizzaPrenotazioniView(LoginRequiredMixin, View):
    def get(self, request):
        if hasattr(request.user, 'paziente'):
            prenotazioni = Prenotazione.objects.filter(paziente=request.user.paziente)
        elif hasattr(request.user, 'terapeuta'):
            prenotazioni = Prenotazione.objects.filter(terapeuta=request.user.terapeuta)
        else:
            messages.error(request, "Accesso negato: non possiedi un profilo paziente o terapeuta.")
            return redirect('home')
        return render(request, 'prenotazioni/visualizza_prenotazioni.html', {'prenotazioni': prenotazioni})

class VisualizzaDisponibilitaView(LoginRequiredMixin, View  ):
    def get(self, request):
        disponibilita = Disponibilita.objects.all()
        return render(request, 'prenotazioni/visualizza_disponibilita.html', {'disponibilita': disponibilita})

class VisualizzaAssenzeView(LoginRequiredMixin, View):
    def get(self, request):
        assenze = Assenza.objects.all()
        return render(request, 'prenotazioni/visualizza_assenze.html', {'assenze': assenze})

# Rimuovi "import json" in cima al file se non ti serve per altro

class ProfiloPrenotaView(LoginRequiredMixin, View):
    def get(self, request, terapeuta_id):
        terapeuta = get_object_or_404(Terapeuta, id=terapeuta_id)
        studi = terapeuta.studi.all()

        giorni_attivi_per_studio = {}
        
        for studio in studi:
            turni = Disponibilita.objects.filter(terapeuta=terapeuta, studio=studio)
            giorni_js = [(turno.giorno + 1) % 7 for turno in turni]
            giorni_attivi_per_studio[studio.id] = list(set(giorni_js))

        context = {
            'terapeuta': terapeuta,
            'studi': studi,
            # CAMBIA QUESTA RIGA: Passa il dizionario Python puro!
            'mappa_giorni_json': giorni_attivi_per_studio 
        }
        return render(request, 'prenotazioni/profilo_prenota.html', context)

class EliminaPrenotazioneView(LoginRequiredMixin, View):
    def post(self, request, prenotazione_id):
        try:
            prenotazione = Prenotazione.objects.get(id=prenotazione_id)
            if hasattr(request.user, 'paziente') or hasattr(request.user, 'terapeuta'):
                if prenotazione.paziente == request.user.paziente or prenotazione.terapeuta == request.user.terapeuta:
                    prenotazione.delete()
                    messages.success(request, "Prenotazione eliminata con successo.")
                else:
                    messages.error(request, "Accesso negato: non puoi eliminare questa prenotazione.")
            else:
                messages.error(request, "Accesso negato: non possiedi un profilo paziente o terapeuta.")
        except Prenotazione.DoesNotExist:
            messages.error(request, "Prenotazione non trovata.")
        return redirect('prenotazioni:visualizza_prenotazioni')

class EliminaDisponibilitaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Accesso negato.")
            return redirect('home')

        # 1. Cerca il turno specifico. 
        # Sicurezza: imponiamo che il 'terapeuta' debba essere quello loggato!
        turno = get_object_or_404(Disponibilita, pk=pk, terapeuta=request.user.terapeuta)
        
        # 2. Distruzione!
        turno.delete()
        
        # 3. Messaggio di successo e ricarica della pagina
        messages.success(request, "Turno eliminato con successo.")
        return redirect('prenotazioni:visualizza_disponibilita')

