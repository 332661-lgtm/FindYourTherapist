🧠 PsyApp - Piattaforma per Sedute Psicologiche
📖 Descrizione del Progetto
PsyApp è un'applicazione web progettata per semplificare e ottimizzare l'incontro tra professionisti della salute mentale e pazienti. La piattaforma offre un ecosistema completo che va dalla ricerca del professionista ideale, alla gestione del calendario degli appuntamenti, fino all'archiviazione e condivisione sicura di documenti clinici.

👥 Ruoli e Funzionalità Principali
🔍 1. Utente Visitatore (Non Registrato)
Vetrina Terapeuti: Accesso libero alla lista dei professionisti presenti sulla piattaforma.

Filtri di Ricerca Avanzati: Possibilità di filtrare e cercare i terapeuti in base a specifiche esigenze (es. specializzazione, città, tariffa).

Nota: Per procedere con la prenotazione di un colloquio, il sistema richiede la registrazione e la creazione di un Profilo Paziente.

👤 2. Utente Paziente (Registrato)
Gestione Profilo: Modifica e aggiornamento dei propri dati personali.

Prenotazione Flessibile: Scelta del professionista, della sede (studio) e dello slot orario desiderato.

Dashboard Appuntamenti: Interfaccia dedicata per visualizzare lo storico completo dei colloqui, categorizzati in: In programma, Effettuati e Annullati.

Spazio Condiviso (File Sharing): Accesso a una cartella condivisa con il proprio terapeuta per lo scambio di documenti, abilitata previa autorizzazione del medico stesso.

🧑‍⚕️ 3. Utente Terapeuta
Networking: Ricerca e visualizzazione dei profili dei propri colleghi iscritti all'app.

Gestione Multi-Studio: Configurazione indipendente degli orari di disponibilità per ogni singola sede/studio in cui il professionista opera.

Gestione Assenze: Blocco del calendario per ferie o imprevisti, con validazione automatica anti-conflitto.

Dashboard Operativa: Calendario giornaliero degli impegni con notifiche visive per le nuove prenotazioni.

Archivio Clinico Pazienti: Scrivania digitale con lista dei pazienti a carico. Per ogni paziente è disponibile uno storage suddiviso in un'area privata (appunti del medico) e un'area condivisa (scambio file con il paziente).

⚙️ Dettagli Tecnici e Workflow
🔐 Autenticazione e Profili
Registrazione Biforcata: L'interfaccia di login/registrazione distingue i percorsi di onboarding per Pazienti e Terapeuti, richiedendo campi specifici per ognuno.

Associazione Studi: I terapeuti possono registrare nuove sedi lavorative o associarsi a studi clinici già esistenti nel database.

Verifica del Profilo (Spunta Blu): L'affidabilità dei terapeuti è garantita da un badge di verifica (spunta blu). Questo status può essere conferito esclusivamente dall'Amministratore di sistema (Admin) dopo opportune verifiche, garantendo sicurezza per i pazienti.

📅 Motore di Prenotazione e Calendario
Flusso Paziente: Il paziente visualizza il profilo del medico, seleziona uno degli studi associati e il sistema genera dinamicamente gli slot disponibili incrociando l'orario di lavoro del medico con gli appuntamenti già presi.

Notifiche Medico: All'accesso nella dashboard, il terapeuta viene avvisato delle nuove prenotazioni non ancora lette tramite un indicatore visivo (puntino lampeggiante).

Gestione e Override: Entrambe le parti possono annullare un colloquio. Il terapeuta gode inoltre di poteri di override: può modificare data e ora di un appuntamento in totale autonomia, scavalcando i vincoli di disponibilità standard del sistema per venire incontro a casistiche eccezionali.

Blocco Assenze: Il terapeuta può inserire periodi di assenza prolungata. Il sistema impedisce la registrazione dell'assenza qualora vi siano già dei colloqui prenotati in quelle specifiche date, prevenendo incongruenze.

📁 Spazio Clinico e Condivisione File
L'applicazione integra un vero e proprio file manager medico-paziente:

Area Privata (Solo Medico): Spazio di archiviazione per referti, appunti e documenti sensibili invisibili al paziente.

Area Condivisa: Una cartella accessibile ad entrambi. Il terapeuta può inviare file al paziente.

Gestione Permessi Dinamica: Il terapeuta dispone di un interruttore (toggle) per concedere o revocare al paziente il permesso di effettuare l'upload di documenti all'interno dell'area condivisa. Il paziente può interagire con questo spazio direttamente dalla propria dashboard.