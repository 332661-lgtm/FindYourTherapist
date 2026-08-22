document.addEventListener("DOMContentLoaded", function() {
    
    // 1. Recuperiamo la mappa generata dalla Vista Python tramite il tag <script> nascosto
    const dataElement = document.getElementById('mappa-giorni-data');
    if (!dataElement) return; // Evita crash se l'elemento non esiste
    
    const mappaGiorni = JSON.parse(dataElement.textContent);
    
    const radioStudi = document.querySelectorAll('.radio-studio');
    const boxCalendario = document.getElementById('box-calendario');
    const avvisoCalendario = document.getElementById('avviso-calendario');
    const contenitoreSlot = document.getElementById('slot-orari-container');

    // 2. Inizializziamo il Calendario Flatpickr (Spento di default)
    let calendario = flatpickr("#calendario-input", {
        inline: true,           // Mostra il calendario sempre aperto, senza pop-up
        locale: "it",           // Lingua italiana
        minDate: "today",       // Impedisce di prenotare nel passato
        defaultDate: "today",   // Parte da oggi
        disable: [
            function(date) { 
                return true; // All'inizio disabilita TUTTI i giorni
            }
        ],
        onChange: function(selectedDates, dateStr, instance) {
            // QUI PARTIRÀ L'ALGORITMO AL CLICK SUL GIORNO BIANCO
            console.log("Il paziente ha cliccato il giorno:", dateStr);
            contenitoreSlot.innerHTML = `<p style="text-align:center; color: #2e8b57; font-weight:bold;">Ricerca orari disponibili per il ${dateStr}...</p>`;
            
            // TODO: Aggiungeremo qui la chiamata fetch() all'API di Django
        }
    });

    // 3. Logica di interazione: Quando si seleziona uno Studio dai Radio Button
    radioStudi.forEach(radio => {
        radio.addEventListener('change', function() {
            const idStudioSelezionato = this.value;
            // Peschiamo i giorni lavorativi (se non ce ne sono, array vuoto)
            const giorniAttivi = mappaGiorni[idStudioSelezionato] || [];

            // Accendiamo visivamente il box del calendario
            boxCalendario.classList.add('attivo');
            avvisoCalendario.style.display = 'none';
            contenitoreSlot.innerHTML = ''; // Puliamo eventuali vecchi slot

            // Aggiorniamo dinamicamente le regole di Flatpickr
            calendario.set('disable', [
                function(date) {
                    // Flatpickr usa 0=Domenica, 1=Lunedì, ecc.
                    const giornoSettimana = date.getDay();
                    
                    // Disabilita il giorno (ritorna true) SE non è nella lista dei giorni attivi per questo studio
                    return !giorniAttivi.includes(giornoSettimana);
                }
            ]);

            // Forziamo il calendario a rinfrescare l'interfaccia con le nuove regole
            calendario.redraw();
        });
    });
});