from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from utenti.models import Paziente, RelazioneTerapeutica, Terapeuta, Studio
from django.db import IntegrityError

class UtentiModelTest(TestCase):
    """
    TEST LOGICA DI BUSINESS (Black-Box):
    Testiamo i vincoli di sicurezza sui ruoli del database.
    Un utente non può avere contemporaneamente un profilo Paziente e uno Terapeuta.
    """
    def setUp(self):
        # Creiamo un utente "base" nel database di test
        self.user_base = User.objects.create_user(username='utente_ibrido', password='123')

    def test_vincolo_ruolo_esclusivo_paziente(self):
        """Edge Case: Proviamo a creare un Paziente usando un account già registrato come Terapeuta."""
        # 1. Registriamo l'utente come Terapeuta (Azione lecita)
        Terapeuta.objects.create(user=self.user_base)
        
        # 2. Proviamo a forzare la creazione di un profilo Paziente per lo STESSO utente
        paziente_illegale = Paziente(user=self.user_base)
        
        # 3. Ci aspettiamo che il metodo clean() blocchi l'operazione con il messaggio esatto
        with self.assertRaisesMessage(ValidationError, "Sicurezza: Questo utente è già registrato come Terapeuta. Non può avere anche un profilo Paziente."):
            paziente_illegale.clean()
            
    def test_vincolo_ruolo_esclusivo_terapeuta(self):
        """Edge Case: Proviamo a creare un Terapeuta usando un account già registrato come Paziente."""
        Paziente.objects.create(user=self.user_base)
        
        terapeuta_illegale = Terapeuta(user=self.user_base)
        
        with self.assertRaisesMessage(ValidationError, "Sicurezza: Questo utente è già registrato come Paziente. Non può avere anche un profilo Terapeuta."):
            terapeuta_illegale.clean()

    def test_integrita_relazione_terapeutica_duplicata(self):
        """
        EDGE CASE (Database): Il vincolo unique_together in RelazioneTerapeutica 
        deve impedire la creazione di due cartelle radice per la stessa coppia medico-paziente.
        """
        # Creiamo un medico e un paziente fittizi
        user_m = User.objects.create_user(username='medico_rel', password='123')
        user_p = User.objects.create_user(username='paziente_rel', password='123')
        t = Terapeuta.objects.create(user=user_m)
        p = Paziente.objects.create(user=user_p)
        
        # Creiamo la prima relazione (Valida)
        RelazioneTerapeutica.objects.create(terapeuta=t, paziente=p)
        
        # Tentare di creare la seconda deve far scattare un IntegrityError a livello di DB
        with self.assertRaises(IntegrityError):
            RelazioneTerapeutica.objects.create(terapeuta=t, paziente=p)


class VetrinaClientTest(TestCase):
    """
    TEST VISTA (Client Test):
    Verifichiamo l'accessibilità della Vetrina e il funzionamento dei filtri di ricerca.
    """
    def setUp(self):
        self.client = Client()
        
        # Creiamo due terapeuti con tariffe diverse per testare il filtro
        user1 = User.objects.create_user(username='doc_economico', password='123')
        self.t_economico = Terapeuta.objects.create(user=user1, prezzo=50.00)
        
        user2 = User.objects.create_user(username='doc_costoso', password='123')
        self.t_costoso = Terapeuta.objects.create(user=user2, prezzo=120.00)
        
        # Creiamo uno studio e lo associamo al primo terapeuta
        self.studio_pe = Studio.objects.create(citta='Pescara', indirizzo='Via Roma 1')
        self.t_economico.studi.add(self.studio_pe)
        
    def test_vetrina_accessibile_a_tutti_senza_login(self):
        """Verifica che un utente NON loggato possa accedere alla vetrina (Codice 200 OK)."""
        
        url = reverse('utenti:vetrina') 
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'utenti/vetrina.html')
        
    def test_filtro_ricerca_prezzo_massimo(self):
        """Verifica che il filtro 'prezzo_max' escluda i terapeuti troppo costosi."""
        url = reverse('utenti:vetrina')
        
        # Simuliamo un utente che inserisce '60' nel campo del prezzo massimo
        response = self.client.get(url, {'prezzo_max': 60})
        
        self.assertEqual(response.status_code, 200)
        
        # Estraiamo i risultati della ricerca dalla vista
        terapeuti_trovati = response.context['page_obj'].object_list
        
        # Verifichiamo che ci sia il terapeuta da 50€, ma NON quello da 120€
        self.assertIn(self.t_economico, terapeuti_trovati)
        self.assertNotIn(self.t_costoso, terapeuti_trovati)


    def test_filtro_prezzo_con_terapeuta_senza_tariffa(self):
        """
        EDGE CASE: Il filtro prezzo deve mostrare i terapeuti sotto la soglia,
        ma DEVE includere anche i terapeuti che non hanno impostato un prezzo (prezzo=None).
        """
        # Creiamo un terapeuta senza prezzo (prezzo=None)
        user_null = User.objects.create_user(username='doc_senza_prezzo', password='123')
        t_senza_prezzo = Terapeuta.objects.create(user=user_null, prezzo=None)

        url = reverse('utenti:vetrina')
        # Filtriamo per un massimo di 60€
        response = self.client.get(url, {'prezzo_max': 60})
        
        terapeuti_trovati = response.context['page_obj'].object_list
        
        # Ci aspettiamo che t_economico (50€) e t_senza_prezzo (None) ci siano, ma non t_costoso (120€)
        self.assertIn(self.t_economico, terapeuti_trovati)
        self.assertIn(t_senza_prezzo, terapeuti_trovati)
        self.assertNotIn(self.t_costoso, terapeuti_trovati)

    def test_sicurezza_spionaggio_ruoli_incrociati(self):
        """
        EDGE CASE: Un Paziente loggato tenta di accedere al pannello esclusivo del Terapeuta.
        Il sistema deve bloccarlo e reindirizzarlo alla home.
        """
        # 1. Creiamo e logghiamo un PAZIENTE
        user_paz = User.objects.create_user(username='paziente_spione', password='123')
        Paziente.objects.create(user=user_paz)
        self.client.login(username='paziente_spione', password='123')
        
        # 2. Il paziente tenta di accedere alla dashboard del TERAPEUTA!
        url_proibito = reverse('utenti:profilo_terapeuta')
        response = self.client.get(url_proibito)
        
        # 3. Verifichiamo che venga rimbalzato alla home (Redirect 302)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_sanitizzazione_spazi_vuoti_nuovo_studio(self):
        """
        EDGE CASE: Il terapeuta tenta di aggiungere uno studio passando solo spazi vuoti.
        La logica .strip() deve intercettarlo e generare un errore.
        """
        # Logghiamo un terapeuta per usare la sua funzione
        self.client.login(username='doc_economico', password='123')
        url_studio = reverse('utenti:aggiungi_studio')
        
        # Inviamo un modulo con soli spazi
        response = self.client.post(url_studio, {
            'citta': '     ',
            'indirizzo': '     '
        })
        
        # La vista non crea lo studio e ricarica la pagina (status 200) mostrando l'errore
        self.assertEqual(response.status_code, 200)
        
        # Verifichiamo che lo studio "spazio vuoto" NON sia stato salvato nel database
        studi_creati = Studio.objects.filter(citta='')
        self.assertEqual(studi_creati.count(), 0)

    def test_profilo_prenota_terapeuta_senza_studi(self):
        """
        EDGE CASE (Resilienza UI): Un paziente visita il profilo di un medico appena registrato
        che non ha ancora associato nessuno Studio al proprio account.
        La vista non deve crashare con IndexError o AttributeError.
        """
        # Creiamo un terapeuta "vuoto"
        user_nuovo = User.objects.create_user(username='doc_nuovo', password='123')
        t_nuovo = Terapeuta.objects.create(user=user_nuovo)
        
        # Logghiamo un paziente per poter accedere alla pagina di prenotazione
        user_paz = User.objects.create_user(username='paz_test2', password='123')
        Paziente.objects.create(user=user_paz)
        self.client.login(username='paz_test2', password='123')
        
        # Visitiamo il suo profilo
        url = reverse('prenotazioni:profilo_prenota', args=[t_nuovo.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # La mappa dei giorni attivi deve essere un dizionario vuoto senza far esplodere Python
        self.assertEqual(response.context['mappa_giorni_json'], {})

    def test_vetrina_filtri_combinati_zero_risultati(self):
        """
        EDGE CASE (Filtri): L'utente applica combinazioni di filtri estreme che non matchano
        nessun terapeuta. Verifichiamo che la vista restituisca 200 OK con una lista vuota,
        invece di generare un errore nella paginazione.
        """
        url = reverse('utenti:vetrina')
        
        # Filtriamo per una città inesistente E un prezzo molto basso
        response = self.client.get(url, {
            'citta': 'Atlantide',
            'prezzo_max': 5.00
        })
        
        self.assertEqual(response.status_code, 200)
        
        # La lista dei risultati deve essere rigorosamente vuota
        terapeuti_trovati = response.context['page_obj'].object_list
        self.assertEqual(len(terapeuti_trovati), 0)
        
        # Nel template deve comparire la stringa di fallback per l'assenza di risultati
        self.assertContains(response, "Nessun risultato trovato")