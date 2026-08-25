import json
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from .models import Assenza, Prenotazione, Disponibilita
from utenti.models import Terapeuta, Paziente, RelazioneTerapeutica, CartellaFile, Documento 
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
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Accesso negato: non possiedi un profilo terapeuta.")
            return redirect('home')
        
        # Filtriamo solo le assenze del medico loggato e le ordiniamo dalla più recente
        assenze = Assenza.objects.filter(terapeuta=request.user.terapeuta).order_by('-data_inizio')
        return render(request, 'prenotazioni/visualizza_assenze.html', {'assenze': assenze})

class EliminaAssenzaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Accesso negato.")
            return redirect('home')

        # Cerchiamo l'assenza assicurandoci che appartenga al medico che ha fatto la richiesta
        assenza = get_object_or_404(Assenza, pk=pk, terapeuta=request.user.terapeuta)
        assenza.delete()
        
        messages.success(request, "Assenza annullata con successo. Il calendario è stato sbloccato per quelle date.")
        return redirect('prenotazioni:visualizza_assenze')

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

class ListaPazientiTerapeutaView(LoginRequiredMixin, View):
    def get(self, request):
        if not hasattr(request.user, 'terapeuta'):
            return redirect('home')

        terapeuta = request.user.terapeuta
        query = request.GET.get('q', '')
        ora_attuale = timezone.now()

        colloqui_futuri = Prenotazione.objects.filter(terapeuta=terapeuta, data_ora__gte=ora_attuale).order_by('data_ora')
        colloqui_passati = Prenotazione.objects.filter(terapeuta=terapeuta, data_ora__lt=ora_attuale).order_by('-data_ora')
        pazienti = Paziente.objects.filter(prenotazioni__terapeuta=terapeuta).distinct()

        if query:
            pazienti = pazienti.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))

        pazienti = pazienti.prefetch_related(
            Prefetch('prenotazioni', queryset=colloqui_futuri, to_attr='futuri'),
            Prefetch('prenotazioni', queryset=colloqui_passati, to_attr='passati')
        )

        paginator = Paginator(pazienti, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # MAGIA: Attacchiamo i file e i permessi direttamente ai pazienti
        for paziente in page_obj:
            rel = RelazioneTerapeutica.objects.filter(terapeuta=terapeuta, paziente=paziente).first()
            if rel:
                paziente.permesso_upload = rel.paziente_puo_caricare_file
                paziente.cartella_privata = CartellaFile.objects.filter(relazione=rel, is_condivisa=False, cartella_padre__isnull=True).prefetch_related('documenti', 'sottocartelle__documenti').first()
                paziente.cartella_condivisa = CartellaFile.objects.filter(relazione=rel, is_condivisa=True, cartella_padre__isnull=True).prefetch_related('documenti', 'sottocartelle__documenti').first()
            else:
                paziente.permesso_upload = False

        query_dict = request.GET.copy()
        if 'page' in query_dict:
            del query_dict['page']

        context = {
            'page_obj': page_obj,
            'query': query,
            'url_params': query_dict.urlencode()
        }
        return render(request, 'prenotazioni/lista_pazienti.html', context)


# LE NUOVE API PER LA GESTIONE FILE
class EliminaDocumentoView(LoginRequiredMixin, View):
    def post(self, request, doc_id):
        doc = get_object_or_404(Documento, id=doc_id)
        # Sicurezza: solo il proprietario del file o il medico possono eliminarlo
        if doc.caricato_da == request.user or hasattr(request.user, 'terapeuta'):
            doc.file.delete() # Elimina il file fisico
            doc.delete()      # Elimina il record nel DB
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Non autorizzato'})

class CreaCartellaView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        paziente_id = data.get('paziente_id')
        is_condivisa = data.get('is_condivisa')
        nome_cartella = data.get('nome')

        # 1. Trova la relazione oppure creala al volo per i nuovi pazienti
        relazione, _ = RelazioneTerapeutica.objects.get_or_create(
            terapeuta=request.user.terapeuta, 
            paziente_id=paziente_id
        )
        
        # 2. Trova la cartella padre (Root) oppure creala al volo
        nome_root = "Condivisa" if is_condivisa else "Privata"
        cartella_padre, _ = CartellaFile.objects.get_or_create(
            relazione=relazione, 
            is_condivisa=is_condivisa, 
            cartella_padre__isnull=True,
            defaults={'nome': nome_root} # Se non esiste, chiamala così
        )
        
        # 3. Crea finalmente la sottocartella richiesta
        CartellaFile.objects.create(
            nome=nome_cartella,
            relazione=relazione,
            cartella_padre=cartella_padre,
            is_condivisa=is_condivisa
        )
        return JsonResponse({'success': True})

class TogglePermessoView(LoginRequiredMixin, View):
    def post(self, request):
        if not hasattr(request.user, 'terapeuta'):
            return JsonResponse({'success': False, 'error': 'Non autorizzato'})
        
        data = json.loads(request.body)
        paziente_id = data.get('paziente_id')
        stato = data.get('stato')
        
        # Cerca la relazione medico-paziente o la crea se è il primo incontro
        relazione, created = RelazioneTerapeutica.objects.get_or_create(
            terapeuta=request.user.terapeuta,
            paziente_id=paziente_id
        )
        relazione.paziente_puo_caricare_file = stato
        relazione.save()
        
        return JsonResponse({'success': True})

class UploadFileView(LoginRequiredMixin, View):
    def post(self, request):
        if not hasattr(request.user, 'terapeuta') and not hasattr(request.user, 'paziente'):
            return JsonResponse({'success': False})

        paziente_id = request.POST.get('paziente_id')
        is_condivisa = request.POST.get('is_condivisa') == 'true'
        cartella_id = request.POST.get('cartella_id')
        files = request.FILES.getlist('file')
        
        # 1. Generazione automatica e sicura della relazione per i nuovi account
        if hasattr(request.user, 'terapeuta'):
            relazione, _ = RelazioneTerapeutica.objects.get_or_create(
                terapeuta=request.user.terapeuta, 
                paziente_id=paziente_id
            )
        else:
            relazione, _ = RelazioneTerapeutica.objects.get_or_create(
                paziente=request.user.paziente, 
                terapeuta_id=request.POST.get('terapeuta_id')
            )
        
        # 2. Assegnazione sicura della cartella
        if cartella_id:
            cartella = CartellaFile.objects.get(id=cartella_id, relazione=relazione)
        else:
            nome_root = "Condivisa" if is_condivisa else "Privata"
            cartella, _ = CartellaFile.objects.get_or_create(
                relazione=relazione, 
                is_condivisa=is_condivisa, 
                cartella_padre__isnull=True,
                defaults={'nome': nome_root}
            )
        
        # 3. Salvataggio
        for f in files:
            Documento.objects.create(cartella=cartella, file=f, nome_originale=f.name, caricato_da=request.user)
            
        return JsonResponse({'success': True})

class EliminaCartellaView(LoginRequiredMixin, View):
    def post(self, request, cartella_id):
        if not hasattr(request.user, 'terapeuta'):
            return JsonResponse({'success': False})
            
        cartella = get_object_or_404(CartellaFile, id=cartella_id)
        # Il medico che ha in cura il paziente può eliminare le cartelle
        if cartella.relazione.terapeuta == request.user.terapeuta:
            cartella.delete() # Questo eliminerà in automatico anche i file dentro grazie al DB in cascata!
            return JsonResponse({'success': True})
            
        return JsonResponse({'success': False})

class CartellaPazienteView(LoginRequiredMixin, View):
    def get(self, request):
        if not hasattr(request.user, 'paziente'):
            messages.error(request, "Accesso riservato ai pazienti.")
            return redirect('home')
        
        paziente = request.user.paziente
        
        # Peschiamo tutti i terapeuti con cui il paziente ha una cartella aperta
        relazioni = RelazioneTerapeutica.objects.filter(paziente=paziente).select_related('terapeuta__user')
        
        # Per ogni relazione, peschiamo la cartella condivisa principale e i suoi file
        for rel in relazioni:
            rel.cartella_condivisa = CartellaFile.objects.filter(
                relazione=rel, 
                is_condivisa=True, 
                cartella_padre__isnull=True
            ).prefetch_related('documenti', 'sottocartelle__documenti').first()
            
        return render(request, 'prenotazioni/cartella_paziente.html', {'relazioni': relazioni})