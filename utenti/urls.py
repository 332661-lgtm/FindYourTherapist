from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (AggiungiStudioView, ProfiloPazienteView, ProfiloTerapeutaView, 
                    RegistrazionePazienteView, RegistrazioneTerapeutaView, VetrinaTerapeutiView, ModificaStudioView)

app_name = 'utenti' 

urlpatterns = [
    path('vetrina/', VetrinaTerapeutiView.as_view(), name='vetrina'),
    path('accedi/', auth_views.LoginView.as_view(template_name='utenti/accedi.html'), name='accedi'),
    path('registrati/', RegistrazionePazienteView.as_view(), name='registrati'),
    path('registrati-terapeuta/', RegistrazioneTerapeutaView.as_view(), name='registrati_terapeuta'),
    path('profilo/', ProfiloPazienteView.as_view(), name='profilo_paziente'),
    path('profilo-terapeuta/', ProfiloTerapeutaView.as_view(), name='profilo_terapeuta'),
    path('aggiungi-studio/', AggiungiStudioView.as_view(), name='aggiungi_studio'),
    path('modifica-studio/<int:studio_id>/', ModificaStudioView.as_view(), name='modifica_studio'),
]