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

document.addEventListener("DOMContentLoaded", function() {
    
    // 1. ELIMINAZIONE FILE (Solo i propri)
    const btnElimina = document.querySelectorAll('.btn-elimina-file');
    btnElimina.forEach(btn => {
        btn.addEventListener('click', function() {
            if(confirm("Sei sicuro di voler eliminare questo file?")) {
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
                        alert("Errore: " + data.error);
                    }
                });
            }
        });
    });

    // 2. UPLOAD FILE (Specifico per il paziente, usa terapeuta_id)
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
            
            const terapeutaId = zone.dataset.terapeutaId; // La differenza chiave dal JS del medico!
            const cartellaId = zone.dataset.cartellaId || '';

            const formData = new FormData();
            formData.append('terapeuta_id', terapeutaId);
            formData.append('is_condivisa', 'true'); // Dal lato paziente è SEMPRE condivisa
            formData.append('cartella_id', cartellaId);
            
            for(let i=0; i < files.length; i++){
                formData.append('file', files[i]);
            }

            const testoOriginale = zone.innerHTML;
            zone.innerHTML = `<span style="color:#2e8b57;">⏳ Caricamento in corso...</span>`;

            fetch('/prenotazioni/api/upload-file/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    zone.innerHTML = `✅ Fatto!`;
                    setTimeout(() => location.reload(), 1000);
                } else {
                    alert('Errore nel caricamento.');
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
});