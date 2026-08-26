from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .forms import (
    RegistrazionePazienteForm, 
    RegistrazioneTerapeutaForm,
    UserUpdateForm, 
    PazienteUpdateForm, 
    TerapeutaUpdateForm
)

# Importiamo i modelli
from .models import Paziente, Terapeuta, Studio, Specializzazione


class RegistrazionePazienteView(View):
    def get(self, request):
        form = RegistrazionePazienteForm()
        return render(request, 'utenti/registrazione_paz.html', {'form': form})

    def post(self, request):
        form = RegistrazionePazienteForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    nuovo_user = form.save(commit=False)
                    nuovo_user.set_password(form.cleaned_data['password'])
                    nuovo_user.save()

                    Paziente.objects.create(
                        user=nuovo_user,
                        numero_telefono=form.cleaned_data['numero_telefono'],
                        data_nascita=form.cleaned_data['data_nascita'],
                        indirizzo=form.cleaned_data['indirizzo']
                    )

                messages.success(request, "Registrazione completata con successo! Benvenuto in FindYourTherapist.")
                return redirect('utenti:accedi')

            except Exception as e:
                messages.error(request, f"Errore critico del database: {e}")
        else:
            messages.error(request, "Attenzione: la registrazione è fallita. Correggi gli errori indicati.")

        return render(request, 'utenti/registrazione_paz.html', {'form': form})


class RegistrazioneTerapeutaView(View):
    def get(self, request):
        form = RegistrazioneTerapeutaForm()
        return render(request, 'utenti/registrazione_ter.html', {'form': form})

    def post(self, request):
        form = RegistrazioneTerapeutaForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Creazione Utente base in RAM
                    user = form.save(commit=False)
                    # Hashing della password
                    user.set_password(form.cleaned_data['password'])
                    user.save()

                    # 2. Creazione del profilo Terapeuta
                    Terapeuta.objects.create(
                        user=user,
                        numero_telefono=form.cleaned_data.get('numero_telefono')
                    )

                messages.success(request, "Registrazione Terapeuta completata! Ora puoi accedere e completare il tuo profilo.")
                return redirect('utenti:accedi')
                
            except Exception as e:
                messages.error(request, "Errore durante la registrazione. Riprova.")
        
        return render(request, 'utenti/registrazione_ter.html', {'form': form})


class VetrinaTerapeutiView(View):
    def get(self, request):
        # Partiamo con tutti i terapeuti
        terapeuti = Terapeuta.objects.all()

        citta_scelta = request.GET.get('citta')
        spec_scelte = request.GET.getlist('specializzazione')
        prezzo_max = request.GET.get('prezzo_max')

        # FILTRO CITTÀ
        if citta_scelta:
            terapeuti = terapeuti.filter(studi__citta__icontains=citta_scelta).distinct()
        
        # FILTRO SPECIALIZZAZIONI
        if spec_scelte:
            terapeuti = terapeuti.filter(specializzazioni__id__in=spec_scelte).distinct()
        
        # FILTRO PREZZO
        if prezzo_max:
            # Usiamo Q per dire: "Prezzo minore o uguale a prezzo_max" OPPURE (|) "Prezzo è nullo"
            terapeuti = terapeuti.filter(
                Q(prezzo__lte=prezzo_max) | Q(prezzo__isnull=True)
            ).distinct()

        # Prepariamo i dati per ricaricare il form
        specializzazioni = Specializzazione.objects.all()
        citta_disponibili = Studio.objects.values_list('citta', flat=True).distinct()

        # 1. Suddividiamo a gruppi di 50
        paginator = Paginator(terapeuti, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # 2. Salviamo gli attuali filtri di ricerca rimuovendo 'page' per non duplicarlo
        query_dict = request.GET.copy()
        if 'page' in query_dict:
            del query_dict['page']
        url_params = query_dict.urlencode()

        context = {
            'page_obj': page_obj,  
            'url_params': url_params,
            'specializzazioni': specializzazioni,
            'citta_disponibili': citta_disponibili,
            'valori_scelti': {
                'citta': citta_scelta or '',
                'specializzazioni': [int(s) for s in spec_scelte] if spec_scelte else [],
                'prezzo_max': prezzo_max or ''
            }
        }
        
        return render(request, 'utenti/vetrina.html', context)


class ProfiloPazienteView(LoginRequiredMixin, View):
    def get(self, request):
        # Sicurezza: Controlla che l'utente loggato sia effettivamente un Paziente
        if not hasattr(request.user, 'paziente'):
            messages.error(request, "Accesso negato: non possiedi un profilo paziente.")
            return redirect('home')

        # Istanziamo i due form riempiendoli con i dati ATTUALI dell'utente (instance=...)
        user_form = UserUpdateForm(instance=request.user)
        paziente_form = PazienteUpdateForm(instance=request.user.paziente)

        context = {
            'user_form': user_form,
            'paziente_form': paziente_form
        }
        return render(request, 'utenti/profilo_paziente.html', context)

    def post(self, request):
        if not hasattr(request.user, 'paziente'):
            return redirect('home')

        # Riceviamo i dati modificati dall'utente
        user_form = UserUpdateForm(request.POST, instance=request.user)
        paziente_form = PazienteUpdateForm(request.POST, instance=request.user.paziente)

        # Se ENTRAMBI i form superano i controlli
        if user_form.is_valid() and paziente_form.is_valid():
            user_form.save()
            paziente_form.save()
            messages.success(request, "Il tuo profilo è stato aggiornato con successo!")
            return redirect('utenti:profilo_paziente')

        # Se c'è un errore, ricarica la pagina mostrando gli errori
        messages.error(request, "Errore nell'aggiornamento. Controlla i dati inseriti.")
        context = {
            'user_form': user_form,
            'paziente_form': paziente_form
        }
        return render(request, 'utenti/profilo_paziente.html', context)


class ProfiloTerapeutaView(LoginRequiredMixin, View):
    def get(self, request):
        if not hasattr(request.user, 'terapeuta'):
            return redirect('home')

        user_form = UserUpdateForm(instance=request.user)
        terapeuta_form = TerapeutaUpdateForm(instance=request.user.terapeuta)
        
        # Estraiamo i dati per costruire l'interfaccia JS personalizzata
        context = {
            'user_form': user_form,
            'terapeuta_form': terapeuta_form,
            'tutte_specializzazioni': Specializzazione.objects.all(),
            'tutti_studi': Studio.objects.all(),
            # Liste degli ID attualmente selezionati dal medico
            'mie_specializzazioni': request.user.terapeuta.specializzazioni.values_list('id', flat=True),
            'miei_studi': request.user.terapeuta.studi.values_list('id', flat=True),
        }
        return render(request, 'utenti/profilo_terapeuta.html', context)
    
    def post(self, request):
        if not hasattr(request.user, 'terapeuta'):
            return redirect('home')

        if request.POST.get('elimina_foto_profilo') == '1':
            if request.user.terapeuta.foto_profilo:
                request.user.terapeuta.foto_profilo.delete(save=False) # Elimina il file dal server
                request.user.terapeuta.foto_profilo = None             # Svuota il database
                request.user.terapeuta.save()

        user_form = UserUpdateForm(request.POST, instance=request.user)
        # Riceviamo i file (request.FILES) con la corretta indentazione
        terapeuta_form = TerapeutaUpdateForm(request.POST, request.FILES, instance=request.user.terapeuta)

        if user_form.is_valid() and terapeuta_form.is_valid():
            user_form.save()
            terapeuta_form.save()
            messages.success(request, "Il tuo profilo professionale è stato aggiornato con successo!")
            return redirect('utenti:profilo_terapeuta')

        messages.error(request, "Errore nell'aggiornamento. Controlla i dati inseriti.")
        context = {
            'user_form': user_form,
            'terapeuta_form': terapeuta_form
        }
        return render(request, 'utenti/profilo_terapeuta.html', context)


class AggiungiStudioView(LoginRequiredMixin, View):
    def get(self, request):
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Accesso negato.")
            return redirect('home')
        return render(request, 'utenti/aggiungi_studio.html')

    def post(self, request):
        if not hasattr(request.user, 'terapeuta'):
            return redirect('home')

        citta = request.POST.get('citta')
        indirizzo = request.POST.get('indirizzo')
        foto = request.FILES.get('foto_studio') # Catturiamo il file dell'immagine

        if citta and indirizzo and citta.strip() and indirizzo.strip():
            nuovo_studio, created = Studio.objects.get_or_create(
                citta=citta.strip().capitalize(),
                indirizzo=indirizzo.strip()
            )
            
            # Se è stata caricata una foto, la assegniamo allo studio
            if foto:
                nuovo_studio.foto_studio = foto
                nuovo_studio.save()
                
            request.user.terapeuta.studi.add(nuovo_studio)
            
            messages.success(request, "Nuova sede registrata e aggiunta al tuo profilo!")
            return redirect('utenti:profilo_terapeuta')
        
        messages.error(request, "Errore: Compila sia la Città che l'Indirizzo con dati validi.")
        return render(request, 'utenti/aggiungi_studio.html')

    from django.shortcuts import get_object_or_404 # Aggiungi questo in cima al file se non c'è

class ModificaStudioView(LoginRequiredMixin, View):
    def get(self, request, studio_id):
        if not hasattr(request.user, 'terapeuta'):
            messages.error(request, "Accesso negato.")
            return redirect('home')
        
        # Peschiamo lo studio
        studio = get_object_or_404(Studio, id=studio_id)
        
        # Sicurezza: verifichiamo che questo studio sia tra quelli del terapeuta
        if studio not in request.user.terapeuta.studi.all():
            messages.error(request, "Non hai i permessi per modificare questa sede.")
            return redirect('utenti:profilo_terapeuta')
            
        return render(request, 'utenti/modifica_studio.html', {'studio': studio})

    def post(self, request, studio_id):
        if not hasattr(request.user, 'terapeuta'):
            return redirect('home')

        studio = get_object_or_404(Studio, id=studio_id)
        if studio not in request.user.terapeuta.studi.all():
            messages.error(request, "Non hai i permessi per modificare questa sede.")
            return redirect('utenti:profilo_terapeuta')

        if request.POST.get('elimina_foto_studio') == '1':
            if studio.foto_studio:
                studio.foto_studio.delete(save=False)
                studio.foto_studio = None
                studio.save()

        citta = request.POST.get('citta')
        indirizzo = request.POST.get('indirizzo')
        foto = request.FILES.get('foto_studio')

        if citta and indirizzo and citta.strip() and indirizzo.strip():
            studio.citta = citta.strip().capitalize()
            studio.indirizzo = indirizzo.strip()
            
            # Se ha caricato una nuova foto, la sostituiamo
            if foto:
                studio.foto_studio = foto
                
            studio.save()
            messages.success(request, "Sede aggiornata con successo!")
            return redirect('utenti:profilo_terapeuta')
        
        messages.error(request, "Errore: Compila sia la Città che l'Indirizzo.")
        return render(request, 'utenti/modifica_studio.html', {'studio': studio})