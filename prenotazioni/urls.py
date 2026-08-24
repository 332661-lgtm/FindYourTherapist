from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    AggiungiPrenotazioneView, AggiungiDisponibilitaView, AggiungiAssenzaView, CartellaPazienteView, NascondiPrenotazioneView,
    OttieniSlotAPIView, UploadFileView, VisualizzaPrenotazioniView, VisualizzaDisponibilitaView,
    EliminaDisponibilitaView, ProfiloPrenotaView, CreaPrenotazioneVeloceView,
    EliminaPrenotazioneView, ModificaPrenotazioneView, ListaPazientiTerapeutaView, TogglePermessoView, 
    CreaCartellaView, EliminaDocumentoView, EliminaCartellaView, VisualizzaAssenzeView, EliminaAssenzaView
)

app_name = 'prenotazioni'

urlpatterns = [
    path('prenotazione/', AggiungiPrenotazioneView.as_view(), name='prenotazione'),
    path('disponibilita/', AggiungiDisponibilitaView.as_view(), name='disponibilita'),
    path('assenza/', AggiungiAssenzaView.as_view(), name='assenza'),
    path('visualizza-prenotazioni/', VisualizzaPrenotazioniView.as_view(), name='visualizza_prenotazioni'),
    path('visualizza-disponibilita/', VisualizzaDisponibilitaView.as_view(), name='visualizza_disponibilita'),
    path('elimina-turno/<int:pk>/', EliminaDisponibilitaView.as_view(), name='elimina_disponibilita'),
    path('visualizza-assenze/', VisualizzaAssenzeView.as_view(), name='visualizza_assenze'),
    path('elimina-assenza/<int:pk>/', EliminaAssenzaView.as_view(), name='elimina_assenza'),
    path('elimina-prenotazione/<int:prenotazione_id>/', EliminaPrenotazioneView.as_view(), name='elimina_prenotazione'),
    path('modifica-prenotazione/<int:pk>/', ModificaPrenotazioneView.as_view(), name='modifica_prenotazione'),
    path('prenota/<int:terapeuta_id>/', ProfiloPrenotaView.as_view(), name='profilo_prenota'),
    path('api/slot-liberi/', OttieniSlotAPIView.as_view(), name='api_slot_liberi'),
    path('conferma-veloce/', CreaPrenotazioneVeloceView.as_view(), name='crea_prenotazione_veloce'),
    path('nascondi-prenotazione/<int:pk>/', NascondiPrenotazioneView.as_view(), name='nascondi_prenotazione'),
    path('i-miei-pazienti/', ListaPazientiTerapeutaView.as_view(), name='lista_pazienti'),
    path('api/toggle-permesso/', TogglePermessoView.as_view(), name='api_toggle_permesso'),
    path('api/upload-file/', UploadFileView.as_view(), name='api_upload_file'),
    path('api/elimina-file/<int:doc_id>/', EliminaDocumentoView.as_view(), name='api_elimina_file'),
    path('api/crea-cartella/', CreaCartellaView.as_view(), name='api_crea_cartella'),
    path('api/elimina-cartella/<int:cartella_id>/', EliminaCartellaView.as_view(), name='api_elimina_cartella'),
    path('i-miei-documenti/', CartellaPazienteView.as_view(), name='cartella_paziente'),
]