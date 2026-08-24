from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Assenza, Prenotazione, Disponibilita
from utenti.models import Terapeuta  # IMPORT CORRETTO QUI
from .forms import AssenzaForm, DisponibilitaForm, PrenotazioneForm, ModificaPrenotazioneForm

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
            prenotazione = form.save(commit=False)
            prenotazione.paziente = request.user.paziente  
            prenotazione.save()
            return redirect('prenotazioni:prenotazione')
        return render(request, 'prenotazioni/prenotazione.html', {'form': form})
    
class AggiungiDisponibilitaView(LoginRequiredMixin, View):
    def get(self, request):
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Accesso negato: non possiedi un profilo terapeuta.")
            return redirect('home')
        form = DisponibilitaForm(terapeuta=request.user.terapeuta)
        return render(request, 'prenotazioni/disponibilita.html', {'form': form}) 

    def post(self, request):
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Accesso negato: non possiedi un profilo terapeuta.")
            return redirect('home')
        form = DisponibilitaForm(request.POST, terapeuta=request.user.terapeuta)
        if form.is_valid():
            form.save()
            messages.success(request, "Disponibilità aggiunta!")
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
            return redirect('prenotazioni:assenza')
        return render(request, 'prenotazioni/assenza.html', {'form': form})

class VisualizzaPrenotazioniView(LoginRequiredMixin, View):
    def get(self, request):
        ora_attuale = timezone.now()

        if hasattr(request.user, 'paziente'):
            prossimi = Prenotazione.objects.filter(paziente=request.user.paziente, data_ora__gte=ora_attuale, stato='in_programma').order_by('data_ora')
            passati = Prenotazione.objects.filter(paziente=request.user.paziente, data_ora__lt=ora_attuale, stato='in_programma',).order_by('-data_ora')
            cancellati = Prenotazione.objects.filter(paziente=request.user.paziente, stato='cancellata', nascosta_paziente=False).order_by('-data_ora')
            tipo_utente = 'paziente'
            nuovi_id = []

        elif hasattr(request.user, 'terapeuta'):
            terapeuta = request.user.terapeuta
            non_lette = Prenotazione.objects.filter(terapeuta=terapeuta, letta_da_medico=False, stato='in_programma')
            conteggio_nuove = non_lette.count()
            nuovi_id = list(non_lette.values_list('id', flat=True))
            
            if conteggio_nuove > 0:
                messaggio = "Hai 1 nuovo colloquio prenotato!" if conteggio_nuove == 1 else f"Hai {conteggio_nuove} nuovi colloqui prenotati!"
                messages.info(request, messaggio)
                non_lette.update(letta_da_medico=True)

            prossimi = Prenotazione.objects.filter(terapeuta=terapeuta, data_ora__gte=ora_attuale, stato='in_programma').order_by('data_ora')
            passati = Prenotazione.objects.filter(terapeuta=terapeuta, data_ora__lt=ora_attuale, stato='in_programma').order_by('-data_ora')
            cancellati = Prenotazione.objects.filter(terapeuta=terapeuta, stato='cancellata', nascosta_terapeuta=False).order_by('-data_ora')
            tipo_utente = 'terapeuta'
            
        else:
            messages.error(request, "Accesso negato: profilo non riconosciuto.")
            return redirect('home')

        context = {
            'prossimi': prossimi, 'passati': passati, 'cancellati': cancellati,
            'tipo_utente': tipo_utente, 'nuovi_id': nuovi_id
        }
        return render(request, 'prenotazioni/visualizza_prenotazioni.html', context)

class VisualizzaDisponibilitaView(LoginRequiredMixin, View):
    def get(self, request):
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Accesso negato: non possiedi un profilo terapeuta.")
            return redirect('home')
        disponibilita = Disponibilita.objects.filter(terapeuta=request.user.terapeuta).order_by('giorno', 'ora_inizio')
        return render(request, 'prenotazioni/visualizza_disponibilita.html', {'disponibilita': disponibilita})
    
class VisualizzaAssenzeView(LoginRequiredMixin, View):
    def get(self, request):
        assenze = Assenza.objects.all()
        return render(request, 'prenotazioni/visualizza_assenze.html', {'assenze': assenze})

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
            'mappa_giorni_json': giorni_attivi_per_studio 
        }
        return render(request, 'prenotazioni/profilo_prenota.html', context)

class EliminaPrenotazioneView(LoginRequiredMixin, View):
    def post(self, request, prenotazione_id):
        try:
            prenotazione = Prenotazione.objects.get(id=prenotazione_id)
            
            # IL TRUCCO È QUI: confrontiamo direttamente il 'user' associato ai profili!
            if prenotazione.paziente.user == request.user or prenotazione.terapeuta.user == request.user:
                prenotazione.stato = 'cancellata'
                prenotazione.save()
                messages.success(request, "Prenotazione annullata. È stata spostata nella lista dei cancellati.")
            else:
                messages.error(request, "Accesso negato: non puoi annullare questa prenotazione.")
                
        except Prenotazione.DoesNotExist:
            messages.error(request, "Prenotazione non trovata.")
            
        return redirect('prenotazioni:visualizza_prenotazioni')

class EliminaDisponibilitaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Accesso negato.")
            return redirect('home')

        turno = get_object_or_404(Disponibilita, pk=pk, terapeuta=request.user.terapeuta)
        turno.delete()
        messages.success(request, "Turno eliminato con successo.")
        return redirect('prenotazioni:visualizza_disponibilita')

class OttieniSlotAPIView(View):
    def get(self, request):
        terapeuta_id = request.GET.get('terapeuta_id')
        studio_id = request.GET.get('studio_id')
        data_str = request.GET.get('data') 

        data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
        giorno_settimana = data_obj.weekday()

        turni = Disponibilita.objects.filter(terapeuta_id=terapeuta_id, studio_id=studio_id, giorno=giorno_settimana)
        prenotazioni_esistenti = Prenotazione.objects.filter(terapeuta_id=terapeuta_id, data_ora__date=data_obj, stato='in_programma')
        
        slot_disponibili = []
        durata_richiesta = timedelta(minutes=60)

        for turno in turni:
            inizio_corrente = datetime.combine(data_obj, turno.ora_inizio)
            fine_turno = datetime.combine(data_obj, turno.ora_fine)

            while inizio_corrente + durata_richiesta <= fine_turno:
                sovrapposizione = False
                
                for p in prenotazioni_esistenti:
                    p_inizio = p.data_ora.replace(tzinfo=None) 
                    p_fine = p_inizio + timedelta(minutes=p.durata_minuti)

                    if inizio_corrente < p_fine and (inizio_corrente + durata_richiesta) > p_inizio:
                        sovrapposizione = True
                        break
                
                if not sovrapposizione:
                    slot_disponibili.append(inizio_corrente.strftime('%H:%M'))
                
                inizio_corrente += timedelta(hours=1) 

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

        data_ora_naive = datetime.strptime(f"{data_str} {ora_str}", "%Y-%m-%d %H:%M")
        data_ora_ufficiale = timezone.make_aware(data_ora_naive)

        Prenotazione.objects.create(
            paziente=request.user.paziente,
            terapeuta=terapeuta,
            data_ora=data_ora_ufficiale,
            durata_minuti=60 
        )
        
        messages.success(request, f"Richiesta inviata! Attendi la conferma dal Dott. {terapeuta.user.last_name}.")
        return redirect('utenti:vetrina')

class ModificaPrenotazioneView(LoginRequiredMixin, View):
    def get(self, request, pk):
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Azione riservata al medico.")
            return redirect('prenotazioni:visualizza_prenotazioni')
        
        prenotazione = get_object_or_404(Prenotazione, pk=pk, terapeuta=request.user.terapeuta, stato='in_programma')
        form = ModificaPrenotazioneForm(instance=prenotazione)
        return render(request, 'prenotazioni/modifica_prenotazione.html', {'form': form, 'prenotazione': prenotazione})

    def post(self, request, pk):
        if not hasattr(request.user, 'terapeuta'):
            return redirect('prenotazioni:visualizza_prenotazioni')
            
        prenotazione = get_object_or_404(Prenotazione, pk=pk, terapeuta=request.user.terapeuta, stato='in_programma')
        form = ModificaPrenotazioneForm(request.POST, instance=prenotazione)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Data e ora modificate con successo!")
            return redirect('prenotazioni:visualizza_prenotazioni')
            
        return render(request, 'prenotazioni/modifica_prenotazione.html', {'form': form, 'prenotazione': prenotazione})

class NascondiPrenotazioneView(LoginRequiredMixin, View):
    def post(self, request, pk):
        prenotazione = get_object_or_404(Prenotazione, pk=pk)
        
        if hasattr(request.user, 'paziente') and prenotazione.paziente == request.user.paziente:
            prenotazione.nascosta_paziente = True
            prenotazione.save()
            
        elif hasattr(request.user, 'terapeuta') and prenotazione.terapeuta == request.user.terapeuta:
            prenotazione.nascosta_terapeuta = True
            prenotazione.save()
            
        return redirect('prenotazioni:visualizza_prenotazioni')