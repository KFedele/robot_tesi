from fastapi import FastAPI, File, Request
from fastapi.responses import FileResponse
from datetime import datetime
import os
import requests

app = FastAPI()

UPLOAD_FOLDER = "C:/Users/katyl/Desktop/Codici_tesi/AcquisizioneDati/Arduino/Mov_Cam_Giro_Misto/uploads"
app.state.UPLOAD_FOLDER = UPLOAD_FOLDER

# Funzione di acquisizione dell'immagine dal server ESP32
def acquisisci_immagine_da_esp32(client_ip: str):
    try:
        # Costruisci l'URL del server ESP32 con l'indirizzo IP del client
        ESP32_URL = f"http://{client_ip}/capture"

        # Effettua la richiesta HTTP per acquisire l'immagine dall'ESP32
        response = requests.get(ESP32_URL)

        # Verifica se la richiesta ha avuto successo (codice di stato 200)
        if response.status_code == 200:
            # Genera un timestamp attuale in millisecondi
            timestamp_attuale = int(datetime.timestamp(datetime.now()) * 1000)

            # Costruisci il nome del file con timestamp UNIX in millisecondi
            nome_file = f"{timestamp_attuale}.jpg"
            percorso_file = os.path.join(UPLOAD_FOLDER, nome_file)

            # Salva l'immagine nel percorso specificato
            with open(percorso_file, 'wb') as file:
                file.write(response.content)

            return percorso_file
        else:
            return None
    except Exception as e:
        print(f"Errore durante l'acquisizione dell'immagine: {str(e)}")
        return None

@app.get("/capture")
async def capture_image(request: Request):
    try:
        # Ottieni l'indirizzo IP del client che ha effettuato la richiesta
        client_ip = request.client.host

        # Chiamare la funzione di acquisizione dell'immagine con l'indirizzo IP del client
        percorso_file = acquisisci_immagine_da_esp32(client_ip)

        if percorso_file:
            # Restituisci la risposta con il percorso del file salvato
            return {"message": "Foto catturata con successo", "file_path": percorso_file}
        else:
            return {"error": "Errore durante l'acquisizione dell'immagine"}
    except Exception as e:
        return {"error": f"Errore: {str(e)}"}

@app.get("/uploads/{file_name}")
async def get_uploaded_file(file_name: str):
    # Restituisci l'immagine dal percorso specificato
    return FileResponse(os.path.join(UPLOAD_FOLDER, file_name), media_type="image/jpeg")
