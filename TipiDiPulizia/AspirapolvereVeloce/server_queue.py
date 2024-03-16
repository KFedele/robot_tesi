from fastapi import FastAPI, HTTPException, File, Request
from pydantic import BaseModel
from queue import Queue
from fastapi.responses import FileResponse
from datetime import datetime
import os
import requests


app = FastAPI()

# Crea una coda per i vettori
vector_queue = Queue()


UPLOAD_FOLDER = "C:/Users/katyl/Desktop/Codici_tesi/MangiaPolvere/AspirapolvereVeloce/uploads"
app.state.UPLOAD_FOLDER = UPLOAD_FOLDER


class VectorRequest(BaseModel):
    pass

class VectorResponse(BaseModel):
    vector: list

def read_vectors_from_file(filename):
    with open(filename, 'r') as file:
        mini_piano_number = None
        vector = []

        for line in file:
            line = line.strip()

            if line.startswith("Mini-piano"):
                if mini_piano_number is not None and vector:
                    vector_queue.put((mini_piano_number, vector))
                    print(f"Added vector for mini-piano {mini_piano_number}: {vector}")
                    vector = []

                mini_piano_number = int(line.split()[1][:-1])  # Rimuovi il carattere ":" dalla fine del numero
                print(f"Lettura di Mini-piano {mini_piano_number}")
            else:
                numbers = line.split()
                try:
                    numbers = [int(num) for num in numbers]
                    vector.extend(numbers)
                except ValueError:
                    print(f"Errore: una o più righe non contengono numeri interi validi.")
                    continue

        if mini_piano_number is not None and vector:
            vector_queue.put((mini_piano_number, vector))
            print(f"Added vector for mini-piano {mini_piano_number}: {vector}")




@app.get("/queue")
async def get_queue():
    vectors = []
    while not vector_queue.empty():
        mini_piano_number, vector = vector_queue.get()
        vectors.append({"mini_piano_number": mini_piano_number, "vector": vector})
    return vectors


@app.post("/add_vector")
async def add_vector(vector: VectorRequest):
    vector_queue.put(vector.vector)
    return {"message": "Vector added successfully"}

@app.get("/get_vector")
async def get_vector():
    if vector_queue.empty():
        raise HTTPException(status_code=404, detail="No vectors available")
    else:
        mini_piano_number, vector = vector_queue.get()
        vector_with_mini_piano_number = {"mini_piano_number": mini_piano_number, "vector": vector}
        vector_with_end_string = vector_with_mini_piano_number.copy()
        vector_with_end_string["vector"].append("END")  # Aggiungi la stringa "END" al vettore
        return vector_with_end_string





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
        print("Server received capture request")
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





if __name__ == "__main__":
    import uvicorn
    # Leggi i vettori dal file di testo al momento dell'avvio dell'applicazione
    read_vectors_from_file("mini_piani.txt")
    uvicorn.run(app, host="0.0.0.0", port=12345)

    
