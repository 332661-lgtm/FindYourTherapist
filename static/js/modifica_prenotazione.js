document.addEventListener("DOMContentLoaded", function() {
    const formModifica = document.querySelector("form");
    const inputDataOra = document.querySelector("input[name='data_ora']");
    
    if (formModifica && inputDataOra) {
        formModifica.addEventListener("submit", function(event) {
            
            const valoreData = inputDataOra.value;
            if (!valoreData) return; 
            
            const dataInizio = new Date(valoreData);
            let minutes = dataInizio.getMinutes();
            let orarioCorretto = false;

            if (minutes !== 0 && minutes !== 30) {
                orarioCorretto = true;
                const roundedMinutes = (Math.round(minutes / 30) * 30) % 60;
                dataInizio.setMinutes(roundedMinutes); 

                const year = dataInizio.getFullYear();
                const month = String(dataInizio.getMonth() + 1).padStart(2, '0');
                const day = String(dataInizio.getDate()).padStart(2, '0');
                const hours = String(dataInizio.getHours()).padStart(2, '0');
                const mins = String(dataInizio.getMinutes()).padStart(2, '0');

                inputDataOra.value = `${year}-${month}-${day}T${hours}:${mins}`;
            }

            // 2. Calcolo della fine (60 minuti dopo)
            const dataFine = new Date(dataInizio.getTime() + (60 * 60000)); 
            
            const orarioInizioForm = dataInizio.toLocaleTimeString('it-IT', {hour: '2-digit', minute:'2-digit'});
            const orarioFineForm = dataFine.toLocaleTimeString('it-IT', {hour: '2-digit', minute:'2-digit'});
            const dataFormattata = dataInizio.toLocaleDateString('it-IT');
            
            let messaggio = "";
            if (orarioCorretto) {
                messaggio = `⚠️ Hai inserito un orario "fuori legge". Il sistema lo ha arrotondato automaticamente alla mezz'ora più vicina.\n\n`;
            }
            
            messaggio += `Stai spostando il colloquio al ${dataFormattata}.\n\nL'appuntamento inizierà alle ${orarioInizioForm} e terminerà alle ${orarioFineForm}.\n\nVuoi confermare le modifiche?`;
            
            const confermato = confirm(messaggio);
            
            if (!confermato) {
                event.preventDefault();
            }
        });
    }
});