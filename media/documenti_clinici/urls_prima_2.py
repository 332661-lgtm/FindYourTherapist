from django.contrib import messages

from django.shortcuts import redirect, render
from .forms import AssenzaForm, DisponibilitaForm, PrenotazioneForm
from django.views import View
from .models import Assenza, Prenotazione, Disponibilita, Terapeuta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone

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
            messages.success(request, "Assenza registrata con successo. Il calendario è stato bloccato.")
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

class VisualizzaDisponibilitaView(LoginRequiredMixin, View):
    def get(self, request):
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Accesso negato: non possiedi un profilo terapeuta.")
            return redirect('home')

        # 1. Filtriamo SOLO i turni del medico loggato (Sicurezza)
        # 2. Li ordiniamo per giorno (0=Lunedì, 1=Martedì) e per orario (Fondamentale per il regroup)
        disponibilita = Disponibilita.objects.filter(
            terapeuta=request.user.terapeuta
        ).order_by('giorno', 'ora_inizio')
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

class OttieniSlotAPIView(View):
    def get(self, request):
        terapeuta_id = request.GET.get('terapeuta_id')
        studio_id = request.GET.get('studio_id')
        data_str = request.GET.get('data') # Arriva come 'YYYY-MM-DD'

        # 1. Parsing della data
        data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
        giorno_settimana = data_obj.weekday() # 0 = Lunedì

        # 2. Peschiamo i turni lavorativi in quel giorno/studio
        turni = Disponibilita.objects.filter(terapeuta_id=terapeuta_id, studio_id=studio_id, giorno=giorno_settimana)
        
        # 3. Peschiamo le prenotazioni GIA' ESISTENTI per quel giorno (per evitare sovrapposizioni)
        prenotazioni_esistenti = Prenotazione.objects.filter(terapeuta_id=terapeuta_id, data_ora__date=data_obj)

        slot_disponibili = []
        durata_richiesta = timedelta(minutes=60) # Il requisito minimo che hai imposto

        # 4. L'ALGORITMO
        for turno in turni:
            # Creiamo l'orario di partenza (es. 09:00)
            inizio_corrente = datetime.combine(data_obj, turno.ora_inizio)
            fine_turno = datetime.combine(data_obj, turno.ora_fine)

            while inizio_corrente + durata_richiesta <= fine_turno:
                sovrapposizione = False
                
                # Controllo contro gli appuntamenti già presi
                for p in prenotazioni_esistenti:
                    # Rimuoviamo il fuso orario solo per fare i calcoli matematici base
                    p_inizio = p.data_ora.replace(tzinfo=None) 
                    p_fine = p_inizio + timedelta(minutes=p.durata_minuti)

                    # Logica di sovrapposizione temporale
                    if inizio_corrente < p_fine and (inizio_corrente + durata_richiesta) > p_inizio:
                        sovrapposizione = True
                        break
                
                if not sovrapposizione:
                    slot_disponibili.append(inizio_corrente.strftime('%H:%M'))
                
                # Avanziamo di mezz'ora come da tua richiesta!
                inizio_corrente += timedelta(hours=1) 

        # Rimuove duplicati e ordina (se il medico ha fatto casini inserendo doppi turni)
        slot_disponibili = sorted(list(set(slot_disponibili)))
        
        return JsonResponse({'slots': slot_disponibili})

class CreaPrenotazioneVeloceView(LoginRequiredMixin, View):
    def post(self, request):
        if not hasattr(request.user, 'paziente'):
            messages.error(request, "Devi essere registrato come paziente per prenotare.")
            return redirect('home')

        terapeuta = get_object_or_404(Terapeuta, id=request.POST.get('terapeuta_id'))
        data_str = request.POST.get('data')
        ora_str = request.POST.get('ora')

        # Assembliamo l'orario e lo rendiamo "ufficiale" per Django (Aware Timezone)
        data_ora_naive = datetime.strptime(f"{data_str} {ora_str}", "%Y-%m-%d %H:%M")
        data_ora_ufficiale = timezone.make_aware(data_ora_naive)

        # Creiamo la richiesta formale (che il medico vedrà in dashboard)
        Prenotazione.objects.create(
            paziente=request.user.paziente,
            terapeuta=terapeuta,
            data_ora=data_ora_ufficiale,
            durata_minuti=60 # Fissato a 1 ora
        )
        
        messages.success(request, f"Richiesta inviata! Attendi la conferma dal Dott. {terapeuta.user.last_name}.")
        return redirect('utenti:vetrina')

class VisualizzaPrenotazioniView(LoginRequiredMixin, View):
    def get(self, request):
        ora_attuale = timezone.now()

        if hasattr(request.user, 'paziente'):
            # Logica Paziente
            prossimi = Prenotazione.objects.filter(
                paziente=request.user.paziente, data_ora__gte=ora_attuale
            ).order_by('data_ora')
            
            passati = Prenotazione.objects.filter(
                paziente=request.user.paziente, data_ora__lt=ora_attuale
            ).order_by('-data_ora') # Ordinamento decrescente (i più recenti prima)
            
            tipo_utente = 'paziente'

        elif hasattr(request.user, 'terapeuta'):
            terapeuta = request.user.terapeuta
            
            # 1. Peschiamo quelle non lette
            non_lette = Prenotazione.objects.filter(terapeuta=terapeuta, letta_da_medico=False)
            conteggio_nuove = non_lette.count()
            
            # 2. TRUCCO: Salviamo gli ID delle nuove in una lista PRIMA di aggiornarle!
            nuovi_id = list(non_lette.values_list('id', flat=True))
            
            if conteggio_nuove > 0:
                if conteggio_nuove == 1:
                    messages.info(request, "Hai 1 nuovo colloquio prenotato dall'ultima volta!")
                else:
                    messages.info(request, f"Hai {conteggio_nuove} nuovi colloqui prenotati!")
                
                # Le marchiamo tutte come lette
                non_lette.update(letta_da_medico=True)

            prossimi = Prenotazione.objects.filter(
                terapeuta=terapeuta, data_ora__gte=ora_attuale
            ).order_by('data_ora')
            
            passati = Prenotazione.objects.filter(
                terapeuta=terapeuta, data_ora__lt=ora_attuale
            ).order_by('-data_ora')
            
            tipo_utente = 'terapeuta'
            
        else:
            messages.error(request, "Accesso negato: profilo non riconosciuto.")
            return redirect('home')

        # Se chi guarda è un paziente, non ci sono "nuovi_id", quindi passiamo una lista vuota
        if tipo_utente == 'paziente':
            nuovi_id = []

        context = {
            'prossimi': prossimi,
            'passati': passati,
            'tipo_utente': tipo_utente,
            'nuovi_id': nuovi_id  # <--- AGGIUNGI QUESTA RIGA
        }
        return render(request, 'prenotazioni/visualizza_prenotazioni.html', context)