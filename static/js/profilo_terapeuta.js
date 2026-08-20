document.addEventListener("DOMContentLoaded", function() {
    
    /* =========================================
       1. LOGICA SPECIALIZZAZIONI (SOLO SELEZIONE)
       ========================================= */
    const specSelect = document.getElementById('spec-select');
    const addSpecBtn = document.getElementById('add-spec-btn');
    const tagsContainer = document.getElementById('tags-container');

    // Aggiunta di una specializzazione
    addSpecBtn.addEventListener('click', function() {
        const option = specSelect.options[specSelect.selectedIndex];
        
        if (!option.value) return; // Ignora se ha scelto il placeholder vuoto

        // Crea il tag
        const tag = document.createElement('div');
        tag.className = 'spec-tag';
        tag.innerHTML = `
            ${option.text} 
            <span class="remove-tag" data-id="${option.value}">×</span>
            <input type="hidden" name="specializzazioni" value="${option.value}">
        `;
        tagsContainer.appendChild(tag);

        // Nasconde l'opzione dal menu a tendina per evitare doppioni
        option.disabled = true;
        option.style.display = 'none';
        specSelect.selectedIndex = 0; // Torna al placeholder
    });

    // Rimozione di una specializzazione (Event Delegation)
    tagsContainer.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-tag')) {
            const specId = e.target.getAttribute('data-id');
            const tagDiv = e.target.parentElement;
            
            // Riabilita l'opzione nel menu a tendina
            const option = specSelect.querySelector(`option[value="${specId}"]`);
            if (option) {
                option.disabled = false;
                option.style.display = '';
            }
            // Elimina il tag
            tagDiv.remove();
        }
    });


    /* =========================================
       2. LOGICA STUDI E MUTUA ESCLUSIONE
       ========================================= */
    const inputCitta = document.getElementById('cerca-citta-studio');
    const boxSuggerimenti = document.getElementById('studi-suggeriti');
    const studioItems = document.querySelectorAll('.studio-suggerito-item');
    
    const inputNuovaCitta = document.getElementById('nuovo_studio_citta_input');
    const inputNuovoIndirizzo = document.querySelector('input[name="nuovo_studio_indirizzo"]');

    // Ricerca asincrona città
    inputCitta.addEventListener('input', function() {
        const testoCercato = this.value.toLowerCase().trim();
        inputNuovaCitta.value = this.value; 
        
        if (testoCercato.length > 2) {
            boxSuggerimenti.style.display = 'block';
            studioItems.forEach(item => {
                const cittaStudio = item.getAttribute('data-citta');
                if (cittaStudio.includes(testoCercato) || item.classList.contains('selezionato')) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        } else {
            let hasSelections = false;
            studioItems.forEach(item => {
                if (item.classList.contains('selezionato')) {
                    item.style.display = 'flex';
                    hasSelections = true;
                } else {
                    item.style.display = 'none';
                }
            });
            boxSuggerimenti.style.display = hasSelections ? 'block' : 'none';
        }
    });

    // Inizializza la visualizzazione se ci sono già dati
    inputCitta.dispatchEvent(new Event('input'));

    // Mutua Esclusione: Controllo Selezione Studio Esistente
    document.getElementById('lista-studi-dinamica').addEventListener('click', function(e) {
        const item = e.target.closest('.studio-suggerito-item');
        if (!item) return;

        const id = item.getAttribute('data-id');
        const checkbox = document.getElementById('chk_studio_' + id);
        const icon = item.querySelector('.status-icon');
        
        checkbox.checked = !checkbox.checked; 
        
        if (checkbox.checked) {
            item.classList.add('selezionato');
            icon.innerText = '✓';
            
            // LOCK: Disabilita il campo nuovo studio
            inputNuovoIndirizzo.value = '';
            inputNuovoIndirizzo.disabled = true;
            inputNuovoIndirizzo.placeholder = "Deseleziona gli studi per crearne uno nuovo";
            inputNuovoIndirizzo.style.backgroundColor = "#e9ecef";
        } else {
            item.classList.remove('selezionato');
            icon.innerText = '+';
            
            // UNLOCK: Se nessun altro studio è selezionato, riabilita
            if (!document.querySelector('.hidden-checkbox:checked')) {
                inputNuovoIndirizzo.disabled = false;
                inputNuovoIndirizzo.placeholder = "Es. Via Ippocrate 4";
                inputNuovoIndirizzo.style.backgroundColor = "";
            }
        }
    });

    // Mutua Esclusione: Se l'utente digita un nuovo studio, deseleziona i vecchi
    inputNuovoIndirizzo.addEventListener('input', function() {
        if (this.value.trim().length > 0) {
            document.querySelectorAll('.hidden-checkbox:checked').forEach(chk => {
                const id = chk.value;
                const item = document.querySelector(`.studio-suggerito-item[data-id="${id}"]`);
                const icon = item.querySelector('.status-icon');
                
                chk.checked = false;
                item.classList.remove('selezionato');
                icon.innerText = '+';
            });
        }
    });
});