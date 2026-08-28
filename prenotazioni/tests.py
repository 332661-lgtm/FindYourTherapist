from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from utenti.models import Terapeuta, Paziente
from prenotazioni.models import Assenza, Prenotazione

class PrenotazioneLogicTest(TestCase):
    """
    TEST REQUISITO 1: Test di una funzione del codice applicativo (Ottica Black-Box)
    Verifichiamo che il sistema riconosca gli appuntamenti sovrapposti.
    """
    def setUp(self):
        # 1. Prepariamo i dati fittizi nel database di test (mock)
        self.user_medico = User.objects.create_user(username='medico_test', password='password123')
        self.user_paziente = User.objects.create_user(username='paziente_test', password='password123')

        self.terapeuta = Terapeuta.objects.create(user=self.user_medico)
        self.paziente = Paziente.objects.create(user=self.user_paziente)

        # Fissiamo una data di test (Domani alle ore 10:00)
        self.data_base = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)

        # Creiamo un appuntamento iniziale valido dalle 10:00 alle 11:00
        self.prenotazione1 = Prenotazione.objects.create(
            paziente=self.paziente,
            terapeuta=self.terapeuta,
            data_ora=self.data_base,
            durata_minuti=60,
            stato='in_programma'
        )

    def test_sovrapposizione_appuntamenti(self):
        """Input NON valido: Inserimento di un appuntamento alle 10:30."""
        prenotazione_errata = Prenotazione(
            paziente=self.paziente,
            terapeuta=self.terapeuta,
            data_ora=self.data_base + timedelta(minutes=30), # 10:30
            durata_minuti=60,
            stato='in_programma'
        )
        # Verifichiamo che chiamando il clean() il sistema "esploda" con un ValidationError
        with self.assertRaises(ValidationError):
            prenotazione_errata.clean()

    def test_appuntamento_valido(self):
        """Input VALIDO: Inserimento di un appuntamento alle 11:30."""
        prenotazione_corretta = Prenotazione(
            paziente=self.paziente,
            terapeuta=self.terapeuta,
            data_ora=self.data_base + timedelta(minutes=90), # 11:30
            durata_minuti=60,
            stato='in_programma'
        )
        # Se il clean() non solleva eccezioni, il test è superato
        try:
            prenotazione_corretta.clean()
        except ValidationError:
            self.fail("La validazione ha bloccato un orario che in realtà era libero!")

    def test_appuntamento_consecutivo_valido(self):
        """Edge Case VALIDO: Appuntamento che inizia nell'istante esatto in cui finisce l'altro."""
        prenotazione_consecutiva = Prenotazione(
            paziente=self.paziente,
            terapeuta=self.terapeuta,
            # Il primo appuntamento è 10:00 - 11:00. Questo inizia esattamente alle 11:00
            data_ora=self.data_base + timedelta(minutes=60), 
            durata_minuti=60,
            stato='in_programma'
        )
        try:
            prenotazione_consecutiva.clean()
        except ValidationError:
            self.fail("Un appuntamento consecutivo (attaccato al precedente) non dovrebbe generare errore!")

    def test_appuntamento_inglobante_invalido(self):
        """Edge Case NON valido: L'appuntamento 'ingloba' interamente uno già esistente."""
        prenotazione_inglobante = Prenotazione(
            paziente=self.paziente,
            terapeuta=self.terapeuta,
            # Inizia alle 09:30 e dura 2 ore (finisce alle 11:30), "mangiandosi" quello delle 10:00
            data_ora=self.data_base - timedelta(minutes=30), 
            durata_minuti=120,
            stato='in_programma'
        )
        with self.assertRaises(ValidationError):
            prenotazione_inglobante.clean()

    def test_sovrapposizione_stesso_paziente_altro_medico(self):
        """Edge Case NON valido: Il paziente prenota un ALTRO medico alla stessa ora."""
        # 1. Creiamo un secondo medico per il test
        user_medico_2 = User.objects.create_user(username='medico2', password='123')
        terapeuta_2 = Terapeuta.objects.create(user=user_medico_2)

        # 2. Il paziente prova a prenotare il medico 2 alla stessa ora del medico 1 (10:00)
        prenotazione_paziente_doppia = Prenotazione(
            paziente=self.paziente,
            terapeuta=terapeuta_2,
            data_ora=self.data_base, 
            durata_minuti=60,
            stato='in_programma'
        )
        
        # assertRaisesMessage controlla non solo che esploda, ma che dia ESATTAMENTE l'errore giusto
        with self.assertRaisesMessage(ValidationError, "Hai già prenotato una seduta in questo orario."):
            prenotazione_paziente_doppia.clean()

    def test_assenza_invalida_con_prenotazione_esistente(self):
        """
        EDGE CASE (Business Logic): Il medico tenta di inserire un'assenza in un giorno 
        in cui ha già un colloquio programmato. Il sistema deve bloccarlo.
        """
        # self.prenotazione1 è già stata creata nel setUp() per domani
        data_colloquio = self.data_base.date()
        
        assenza_illegale = Assenza(
            terapeuta=self.terapeuta,
            data_inizio=data_colloquio,
            data_fine=data_colloquio
        )
        
        # Ci aspettiamo che il metodo clean() dell'Assenza sollevi un ValidationError
        with self.assertRaises(ValidationError):
            assenza_illegale.clean()


class ViewClientTest(TestCase):
    """
    TEST REQUISITO 2: Test di una vista utente tramite il Client di Django
    Verifichiamo le risposte HTTP, la sicurezza e il contenuto della pagina.
    """
    def setUp(self):
        self.client = Client()
        # Creiamo un paziente fittizio per il login
        self.user_paziente = User.objects.create_user(username='paziente_client', password='password123')
        self.paziente = Paziente.objects.create(user=self.user_paziente)

    def test_visualizza_prenotazioni_non_autenticato(self):
        """Verifica che un utente anonimo non possa accedere alla dashboard."""
        url = reverse('prenotazioni:visualizza_prenotazioni')
        response = self.client.get(url)
        
        # Ci aspettiamo un codice 302 (Redirect) verso la pagina di Login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/utenti/accedi/'))

    def test_visualizza_prenotazioni_autenticato(self):
        """Verifica che un paziente loggato veda correttamente la pagina."""
        self.client.login(username='paziente_client', password='password123')
        url = reverse('prenotazioni:visualizza_prenotazioni')
        response = self.client.get(url)
        
        # 1. Verifica lo status HTTP 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # 2. Verifica che stia usando il template HTML corretto
        self.assertTemplateUsed(response, 'prenotazioni/visualizza_prenotazioni.html')
        
        # 3. Verifica che il titolo sia presente nel contenuto (Codice HTML renderizzato)
        self.assertContains(response, 'I Miei Colloqui')

    def test_sicurezza_elimina_prenotazione_altrui(self):
        """EDGE CASE (Sicurezza): Paziente tenta di eliminare appuntamento altrui."""
        # 1. Creiamo un medico fittizio per il test
        user_med = User.objects.create_user(username='doc_vittima', password='123')
        terapeuta = Terapeuta.objects.create(user=user_med)

        # 2. Creiamo il paziente vittima e il suo appuntamento
        user_vittima = User.objects.create_user(username='vittima', password='123')
        paziente_vittima = Paziente.objects.create(user=user_vittima)

        prenotazione_vittima = Prenotazione.objects.create(
            paziente=paziente_vittima,
            terapeuta=terapeuta, 
            data_ora=timezone.now() + timedelta(days=2),
            durata_minuti=60,
            stato='in_programma'
        )

        # 3. Logghiamo l'hacker
        self.client.login(username='paziente_client', password='password123')

        url_elimina = reverse('prenotazioni:elimina_prenotazione', args=[prenotazione_vittima.id])
        self.client.post(url_elimina)

        prenotazione_vittima.refresh_from_db()
        self.assertEqual(prenotazione_vittima.stato, 'in_programma')

    def test_api_slot_giorno_senza_turni(self):
        """
        EDGE CASE (API): L'API degli slot deve restituire una lista vuota (senza crashare)
        se le viene richiesto un giorno in cui il medico non ha registrato alcuna disponibilità.
        """
        # 1. Creiamo un medico fittizio perché in questa classe non esisteva ancora!
        user_med = User.objects.create_user(username='doc_api', password='123')
        terapeuta = Terapeuta.objects.create(user=user_med)

        # 2. Usiamo una data molto lontana per assicurarci che non ci siano turni
        data_vuota = (timezone.now() + timedelta(days=100)).strftime('%Y-%m-%d')
        
        # ATTENZIONE: Qui rimetti il nome esatto della rotta che avevi corretto tu poco fa!
        url_api = reverse('prenotazioni:api_slot_liberi') 
        
        response = self.client.get(url_api, {
            'terapeuta_id': terapeuta.id, # <--- ORA USIAMO L'ID DEL MEDICO APPENA CREATO
            'studio_id': 1, 
            'data': data_vuota
        })
        
        self.assertEqual(response.status_code, 200)
        # Verifichiamo che il JSON restituito sia {'slots': []}
        self.assertEqual(response.json()['slots'], [])

    