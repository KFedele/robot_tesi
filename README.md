# robot_tesi


- In AcquisizioneDati ci sono i codici per l'acquisizione immagini del robot Freenove.
- In AcquisizioneDatiGiroscopio i dati per ricavare le posizioni dal giroscopio e graficarli in rviz2
- In DemoAspirapolvere lo sketch che accetta il percorso ottimo da server e percorre la griglia
- In TaskSchedulingServer ci sarà il server che divide in task i piani assegnandoli a ciascun robot che arriva
- In TipiDiPulizia c'è:

  -la pulizia veloce: il robot richiede dalla coda del server un piano da pulire, lo riceve e mentre lo percorre scatta semplicemente una foto. Il risultato è che alla fine il server avrà le foto per calcolare la nuova 
   reward e ripopolare la coda con il nuovo percorso. Ci saranno anche pulizia media e si spera avanzata.
  -la pulizia media: il robot persiste nelle aree sporche finchè applicando il Machine Learning non verifica che la ricompensa si è abbassata (livello di sporco diminuito sotto una certa soglia regolabile). Una volta 
   terminato il percorso del minipiano singolo, il server ricalcola il path del medesimo minipiano nuovo. Termina il processo di creazione del minipiano quando tutte le reward sono pari a zero.
