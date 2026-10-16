# Gestione Medicine

La nuova interfaccia è disponibile in `gestione_medicine.html`: aprila con un browser moderno su PC o telefono. Non richiede installazione né connessione per gestire l'elenco. I dati sono conservati localmente nel browser/dispositivo; usa **Esporta backup** per salvarne una copia e **Importa backup** per ripristinarla o trasferirla. L'elenco iniziale è vuoto: aggiungi i dati dei tuoi pazienti sul tuo dispositivo.

## Aprire sullo smartphone

Apri **https://rsergione1953.github.io/gestione-medicine/** nel browser del telefono. Per aggiungerla alla schermata iniziale:

- **Android (Chrome):** menu ⋮ > **Installa app** oppure **Aggiungi a schermata Home**.
- **iPhone/iPad (Safari):** **Condividi** > **Aggiungi alla schermata Home**.

Il sito serve il programma, non rimanda al repository. I dati dei pazienti restano nel browser di quel dispositivo e non vengono caricati su GitHub. Per usarli su un altro dispositivo, esporta un backup e importalo lì. Dopo il primo caricamento l'interfaccia può riaprirsi offline; per sincronizzare dispositivi serve invece un servizio online separato.

## Funzioni

- Aggiunta e modifica dei farmaci, delle indicazioni, delle quantità e della soglia di avviso.
- Aggiornamento rapido della scorta, sia impostando un numero preciso sia aggiungendo o togliendo un'unità.
- Avvisi visibili per le scorte pari o inferiori alla soglia. Nell'APK Android, alla prima sottoscorta appare una notifica sonora ad alta priorità che resta finché non premi **Ho capito**; la conferma vale per il singolo farmaco. Il permesso notifiche va autorizzato.
- Stampa dell'elenco completo o dei soli farmaci selezionati. Nella finestra di stampa si può scegliere **Salva come PDF**.
- Ricerca e filtro dei farmaci sottoscorta.
- Filtro per paziente e farmaci raggruppati in sezioni separate.
- Stima dei giorni e della data di esaurimento dalle assunzioni giornaliere inserite.
- Unità di misura e conversione confezione personalizzabili, con aggiunta rapida di una confezione.

La stima è mostrata solo se è stato specificato un consumo giornaliero. La scorta e la dose devono usare la stessa unità di consumo. Per convertire una confezione si inseriscono il contenuto, la sua unità e il fattore di conversione verificato per quello specifico prodotto: per esempio 100 ml × 20 gocce/ml = 2.000 gocce. Non si presume un rapporto universale tra millilitri e gocce o tra grammi e cucchiaini. Per le polveri, configura il numero di misurini/cucchiaini per confezione solo se noto; altrimenti la previsione resta non disponibile. Sono stime indicative, non indicazioni cliniche.

Gli avvisi nel sito sono controllati quando l'app è aperta e i dati cambiano: non sono promemoria programmati in background e non sostituiscono le indicazioni di un medico o farmacista. L'azione Android **Ho capito** con notifica persistente appartiene all'APK nativo, non all'installazione del sito come app web.

## Trasferire i dati dal programma Python

Se il database `non_dimentico.db` esiste, colloca `converti_database.py` nella stessa cartella e avvia:

```powershell
python .\converti_database.py
```

Per indicare altri percorsi:

```powershell
python .\converti_database.py "C:\percorso\non_dimentico.db" --output "C:\percorso\backup-medicine.json"
```

Nell'app HTML scegli **Importa backup** e seleziona il file JSON creato. L'importazione sostituisce l'elenco attuale, quindi esporta prima un backup se vuoi conservarlo.
Il programma Python conserva i dati già presenti nel database, ma non inserisce pazienti o farmaci dimostrativi.

## Progetto Android

La cartella `android-app` contiene il progetto Android Studio che apre la stessa interfaccia HTML, mantiene i dati sul dispositivo e usa il servizio di stampa Android. Per creare l'APK:

1. Installa Android Studio con Android SDK 34 e un JDK 17.
2. Apri la cartella `android-app` in Android Studio e attendi la sincronizzazione Gradle.
3. Seleziona **Build > Build Bundle(s) / APK(s) > Build APK(s)**.

In questa cartella di lavoro non sono disponibili Android SDK/Gradle né il JDK richiesto per compilare; il progetto sorgente è fornito, ma l'APK non è stato generato qui.
