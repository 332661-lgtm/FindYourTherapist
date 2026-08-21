document.addEventListener("DOMContentLoaded", function() {
    
    /* =========================================
       1. LOGICA SPECIALIZZAZIONI (AUTO-AGGIUNTA)
       ========================================= */
    const specSelect = document.getElementById('spec-select');
    const tagsContainer = document.getElementById('tags-container');

    // Appena l'utente seleziona una voce, crea il tag in automatico
    specSelect.addEventListener('change', function() {
        const option = this.options[this.selectedIndex];
        if (!option.value) return; 

        const tag = document.createElement('div');
        tag.className = 'spec-tag';
        tag.innerHTML = `
            ${option.text} 
            <span class="remove-tag" data-id="${option.value}">×</span>
            <input type="hidden" name="specializzazioni" value="${option.value}">
        `;
        tagsContainer.appendChild(tag);

        option.disabled = true;
        option.style.display = 'none';
        this.selectedIndex = 0; // Torna istantaneamente su "Seleziona..."
    });

    tagsContainer.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-tag')) {
            const specId = e.target.getAttribute('data-id');
            const tagDiv = e.target.parentElement;
            
            const option = specSelect.querySelector(`option[value="${specId}"]`);
            if (option) {
                option.disabled = false;
                option.style.display = '';
            }
            tagDiv.remove();
        }
    });

    /* =========================================
       2. LOGICA STUDI
       ========================================= */
    const inputCitta = document.getElementById('cerca-citta-studio');
    const boxSuggerimenti = document.getElementById('studi-suggeriti');
    const studioItems = document.querySelectorAll('.studio-suggerito-item');

    inputCitta.addEventListener('input', function() {
        const testoCercato = this.value.toLowerCase().trim();
        
        if (testoCercato.length > 2) {
            boxSuggerimenti.style.display = 'block';
            studioItems.forEach(item => {
                const cittaStudio = item.getAttribute('data-citta');
                const isChecked = item.querySelector('.studio-checkbox').checked;
                
                if (cittaStudio.includes(testoCercato) || isChecked) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        } else {
            let hasSelections = false;
            studioItems.forEach(item => {
                if (item.querySelector('.studio-checkbox').checked) {
                    item.style.display = 'block';
                    hasSelections = true;
                } else {
                    item.style.display = 'none';
                }
            });
            boxSuggerimenti.style.display = hasSelections ? 'block' : 'none';
        }
    });

    inputCitta.dispatchEvent(new Event('input'));
});