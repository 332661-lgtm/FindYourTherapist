document.addEventListener("DOMContentLoaded", function() {
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
            const studioSelezionato = document.querySelector('.radio-studio:checked');
            if(!studioSelezionato) return;
            document.getElementById('descrizione-container').style.display = 'block';
            contenitoreSlot.innerHTML = `<p style="text-align:center; color: #2e8b57;">Ricerca orari disponibili...</p>`;
            
            // 1. CHIAMATA ALLA NOSTRA API PYTHON
            const url_api = `/prenotazioni/api/slot-liberi/?terapeuta_id=${document.querySelector('[name="terapeuta_id"]').value}&studio_id=${studioSelezionato.value}&data=${dateStr}`;
            
            fetch(url_api)
            .then(response => response.json())
            .then(data => {
                contenitoreSlot.innerHTML = `<h5 style="margin-bottom:10px;">Orari disponibili per il ${dateStr}:</h5>`;
                
                const slotContainer = document.createElement('div');
                slotContainer.style.display = 'grid';
                slotContainer.style.gridTemplateColumns = 'repeat(3, 1fr)';
                slotContainer.style.gap = '10px';

                if(data.slots.length === 0) {
                    contenitoreSlot.innerHTML += `<p style="color:#d9534f;">Nessun orario disponibile per questa data. Riprova in un altro giorno.</p>`;
                    return;
                }

                // 2. CREAZIONE DEI BOTTONI PER OGNI ORARIO
                data.slots.forEach(ora => {
                    const btn = document.createElement('button');
                    btn.className = 'btn-slot-orario'; 
                    btn.textContent = ora;
                    btn.type = 'button';
                    
                    // 3. IL CLICK CHE INVIA LA PRENOTAZIONE (IL POP-UP)
                    btn.onclick = function() {
                        if(confirm(`Sei sicuro di voler inviare la richiesta di prenotazione per le ${ora}? (Durata: 1 ora)`)) {
                            document.getElementById('hidden_studio_id').value = studioSelezionato.value;
                            document.getElementById('hidden_data').value = dateStr;
                            document.getElementById('hidden_ora').value = ora;
                            document.getElementById('hidden_descrizione').value = document.getElementById('descrizione-input').value;
                            document.getElementById('form-conferma-prenotazione').submit();
                        }
                    };
                    slotContainer.appendChild(btn);
                });
                
                contenitoreSlot.appendChild(slotContainer);
            })
            .catch(error => {
                console.error("Errore API:", error);
                contenitoreSlot.innerHTML = `<p style="color:red;">Errore di connessione. Riprova.</p>`;
            });
        }
    });

    // 3. Logica di interazione: Quando si seleziona uno Studio dai Radio Button
    radioStudi.forEach(radio => {
        radio.addEventListener('change', function() {
            const idStudioSelezionato = this.value;
            const giorniAttivi = mappaGiorni[idStudioSelezionato] || [];
            const imgUrl = this.getAttribute('data-img');
            const previewBox = document.getElementById('studio-image-preview');
            const imgTag = document.getElementById('studio-img-tag');

            if (imgUrl && imgUrl.trim() !== '') {
                imgTag.src = imgUrl;
                previewBox.style.display = 'block'; 
            } else {
                previewBox.style.display = 'none';
            }

            boxCalendario.classList.add('attivo');
            avvisoCalendario.style.display = 'none';
            contenitoreSlot.innerHTML = '';

            calendario.set('disable', [
                function(date) {
                    const giornoSettimana = date.getDay();
                    return !giorniAttivi.includes(giornoSettimana);
                }
            ]);

            calendario.redraw();
        });
    });
});