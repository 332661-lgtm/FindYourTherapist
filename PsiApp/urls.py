from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Diciamo a Django: se l'utente va su /home/, mostragli home.html
    path('home/', TemplateView.as_view(template_name='home.html'), name='home'),
    path('utenti/', include('utenti.urls', namespace='utenti')),
    path('prenotazioni/', include('prenotazioni.urls', namespace='prenotazioni')),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)