// Funzione per ottenere il CSRF token di Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Funzione globale e generica per aprire/chiudere le tendine (Annullati / Fatti)
function toggleBox(button) {
    const box = button.parentElement.nextElementSibling;
    const currentText = button.innerHTML;
    if (box.style.display === 'none' || box.style.display === '') {
        box.style.display = 'block';
        button.innerHTML = currentText.replace('+ Mostra', '- Nascondi');
    } else {
        box.style.display = 'none';
        button.innerHTML = currentText.replace('- Nascondi', '+ Mostra');
    }
}

document.addEventListener("DOMContentLoaded", function() {
    
    // 1. GESTIONE TOGGLE SWITCH (Permessi paziente)
    const toggles = document.querySelectorAll('.toggle-permesso');
    toggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const pazienteId = this.dataset.pazienteId;
            const stato = this.checked;

            fetch('/prenotazioni/api/toggle-permesso/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ paziente_id: pazienteId, stato: stato })
            })
            .then(res => res.json())
            .then(data => {
                if(!data.success) {
                    alert('Errore di connessione. Permesso non salvato.');
                    this.checked = !stato; 
                }
            });
        });
    });

    // 2. GESTIONE UPLOAD FILE E DRAG&DROP
    const dropZones = document.querySelectorAll('.drag-drop-zone');
    dropZones.forEach(zone => {
        const fileInput = zone.querySelector('.file-input-nascosto');
        
        zone.addEventListener('click', () => fileInput.click());

        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.style.backgroundColor = '#e8f5e9';
            zone.style.borderColor = '#2e8b57';
        });

        zone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            zone.style.backgroundColor = '';
            zone.style.borderColor = '';
        });

        const processaFile = (files) => {
            if (files.length === 0) return;
            
            const pazienteId = zone.dataset.pazienteId;
            const isCondivisa = zone.dataset.condivisa;
            const cartellaId = zone.dataset.cartellaId || '';

            const formData = new FormData();
            formData.append('paziente_id', pazienteId);
            formData.append('is_condivisa', isCondivisa);
            formData.append('cartella_id', cartellaId);
            for(let i=0; i < files.length; i++){
                formData.append('file', files[i]);
            }

            const testoOriginale = zone.innerHTML;
            zone.innerHTML = `<span style="color:#2e8b57;">⏳ Caricamento di ${files.length} file in corso...</span>`;

            fetch('/prenotazioni/api/upload-file/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    zone.innerHTML = `<span style="color:#2e8b57;">✅ File salvati con successo!</span>`;
                    setTimeout(() => location.reload(), 1000);
                } else {
                    alert('Errore: ' + data.error);
                    zone.innerHTML = testoOriginale;
                }
            });
        };

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.style.backgroundColor = '';
            zone.style.borderColor = '';
            processaFile(e.dataTransfer.files);
        });

        fileInput.addEventListener('change', (e) => {
            processaFile(e.target.files);
        });
    });

    // 3. ELIMINAZIONE FILE
    const btnElimina = document.querySelectorAll('.btn-elimina-file');
    btnElimina.forEach(btn => {
        btn.addEventListener('click', function() {
            if(confirm("Sei sicuro di voler eliminare definitivamente questo file?")) {
                const docId = this.dataset.docId;
                fetch(`/prenotazioni/api/elimina-file/${docId}/`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCookie('csrftoken') }
                })
                .then(res => res.json())
                .then(data => {
                    if(data.success) {
                        this.closest('.colloquio-item').remove();
                    } else {
                        alert("Errore nell'eliminazione.");
                    }
                });
            }
        });
    });

    // 4. CREAZIONE SOTTOCARTELLE
    const btnNuovaCartella = document.querySelectorAll('.btn-nuova-cartella');
    btnNuovaCartella.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const nome = prompt("Inserisci il nome della nuova cartella:");
            if (nome && nome.trim() !== "") {
                const pazienteId = this.dataset.pazienteId;
                const isCondivisa = this.dataset.condivisa === 'true';

                fetch('/prenotazioni/api/crea-cartella/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                    body: JSON.stringify({ paziente_id: pazienteId, is_condivisa: isCondivisa, nome: nome })
                })
                .then(res => res.json())
                .then(data => {
                    if(data.success) {
                        location.reload();
                    } else {
                        alert("Errore nella creazione della cartella.");
                    }
                });
            }
        });
    });

    // 5. ELIMINAZIONE CARTELLA
    const btnEliminaCartella = document.querySelectorAll('.btn-elimina-cartella');
    btnEliminaCartella.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            if(confirm("ATTENZIONE: Eliminando la cartella verranno persi anche tutti i file al suo interno. Procedere?")) {
                const cartellaId = this.dataset.cartellaId;
                fetch(`/prenotazioni/api/elimina-cartella/${cartellaId}/`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCookie('csrftoken') }
                })
                .then(res => res.json())
                .then(data => {
                    if(data.success) {
                        this.closest('details').remove();
                    } else {
                        alert("Errore nell'eliminazione.");
                    }
                });
            }
        });
    });
});