from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    AggiungiPrenotazioneView, AggiungiDisponibilitaView, AggiungiAssenzaView,
    OttieniSlotAPIView, VisualizzaPrenotazioniView, VisualizzaDisponibilitaView,
    EliminaDisponibilitaView, ProfiloPrenotaView, CreaPrenotazioneVeloceView,
    EliminaPrenotazioneView, ModificaPrenotazioneView
)

app_name = 'prenotazioni'

urlpatterns = [
    path('prenotazione/', AggiungiPrenotazioneView.as_view(), name='prenotazione'),
    path('disponibilita/', AggiungiDisponibilitaView.as_view(), name='disponibilita'),
    path('assenza/', AggiungiAssenzaView.as_view(), name='assenza'),
    path('visualizza-prenotazioni/', VisualizzaPrenotazioniView.as_view(), name='visualizza_prenotazioni'),
    path('visualizza-disponibilita/', VisualizzaDisponibilitaView.as_view(), name='visualizza_disponibilita'),
    path('elimina-turno/<int:pk>/', EliminaDisponibilitaView.as_view(), name='elimina_disponibilita'),
    
    # PER L'ELIMINAZIONE SOFT E LA MODIFICA
    path('elimina-prenotazione/<int:prenotazione_id>/', EliminaPrenotazioneView.as_view(), name='elimina_prenotazione'),
    path('modifica-prenotazione/<int:pk>/', ModificaPrenotazioneView.as_view(), name='modifica_prenotazione'),
    
    path('prenota/<int:terapeuta_id>/', ProfiloPrenotaView.as_view(), name='profilo_prenota'),
    path('api/slot-liberi/', OttieniSlotAPIView.as_view(), name='api_slot_liberi'),
    path('conferma-veloce/', CreaPrenotazioneVeloceView.as_view(), name='crea_prenotazione_veloce'),
]