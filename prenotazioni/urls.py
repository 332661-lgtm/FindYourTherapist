from django.urls import path
from django.contrib.auth import views as auth_views
from .views import AggiungiPrenotazioneView, AggiungiDisponibilitaView, AggiungiAssenzaView, VisualizzaPrenotazioniView, VisualizzaDisponibilitaView, EliminaDisponibilitaView, ProfiloPrenotaView
from prenotazioni import views

app_name = 'prenotazioni'

urlpatterns = [
    path('prenotazione/', AggiungiPrenotazioneView.as_view(), name='prenotazione'),
    path('disponibilita/', AggiungiDisponibilitaView.as_view(), name='disponibilita'),
    path('assenza/', AggiungiAssenzaView.as_view(), name='assenza'),
    path('visualizza-prenotazioni/', VisualizzaPrenotazioniView.as_view(), name='visualizza_prenotazioni'),
    path('visualizza-disponibilita/', VisualizzaDisponibilitaView.as_view(), name='visualizza_disponibilita'),
    path('elimina-turno/<int:pk>/', EliminaDisponibilitaView.as_view(), name='elimina_disponibilita'),
    path('prenota/<int:terapeuta_id>/', ProfiloPrenotaView.as_view(), name='profilo_prenota')
]