from fastapi import FastAPI, HTTPException, File, Request, Query
from pydantic import BaseModel
from queue import Queue
from fastapi.responses import FileResponse
from datetime import datetime
import os
import requests
import numpy as np
from optimumPath import optimumPath
import glob

from impFindSingolo import count_imperfections

app = FastAPI()

# Crea una coda per i vettori
vector_queue = Queue()


UPLOAD_FOLDER = "C:/Users/katyl/Desktop/Codici_tesi/MangiaPolvere/AspirapolvereMedio/uploads"
app.state.UPLOAD_FOLDER = UPLOAD_FOLDER
adv_clean=0

num_adv_robot=0

waiting=True
help_requests=0
help_minipiano=0


def split_vector(vector):
    length = len(vector)
    if length % 2 == 0:  # Se la lunghezza del vettore è pari
        mid = length // 2
        first_half = vector[:mid]
        second_half = vector[mid:]
    else:  # Se la lunghezza del vettore è dispari
        mid = length // 2 + 1
        first_half = vector[:mid]
        second_half = vector[mid:]
    return first_half, second_half



def get_subvector_from_value(vector, start_value):
    if start_value in vector:
        start_index = vector.index(start_value)
        return vector[start_index:]
    else:
        return None


def read_matrix_from_file(file_path):
    matrix = []
    with open(file_path, 'r') as file:
        for line in file:
            # Split della riga in valori float
            row = [float(value) for value in line.strip().split()]
            matrix.append(row)
    return np.array(matrix)
    
def write_to_file(mini_piano_number: int, current_position: int, imperfection_count: int):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = os.path.join(UPLOAD_FOLDER, str(mini_piano_number), "log.txt")
    with open(file_path, "a") as file:
        file.write(f"{current_time}, Position: {current_position}, Reward: {imperfection_count}\n")
        
def print_queue(queue):
    temp_queue = list(queue.queue)  # Crea una copia della coda
    for item in temp_queue:
        print(item)



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

def get_vector_from_file(file_name, mini_piano_number):
    target_mini_piano = f"Mini-piano {mini_piano_number}:"
    with open(file_name, 'r') as file:
        for line in file:
            if target_mini_piano in line:
                vector = line.split(":")[1].strip()
                vector = list(map(int, vector.split()))
                return vector
    return None





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
    global num_adv_robot
    if vector_queue.empty():
        if num_adv_robot!=0: #se ci sono robot in pulizia avanzata
            print("In attesa di un robot da aiutare/piano da pulire... ")
            while waiting==True:
                
            print(f"Trovato minipiano n: {help_minipiano} \n Piano di pulizia: {second_half}")
            num_adv_robot -=1 
            vector_with_mini_piano_number = {"mini_piano_number": help_minipiano, "vector": second_half}
            vector_with_end_string = vector_with_mini_piano_number.copy()
            vector_with_end_string["vector"].append("END")  # Aggiungi la stringa "END" al vettore        
            return vector_with_end_string
            
        else:
 
            raise HTTPException(status_code=404, detail="No vectors available")
    else:
        if adv_clean==1:
            num_adv_robot+=1
        mini_piano_number, vector = vector_queue.get()
        log_file_path = f"uploads/{mini_piano_number}/log.txt"
        if os.path.exists(log_file_path):
            os.remove(log_file_path)
        # Cancella i file .jpg
        jpeg_files_path = f"uploads/{mini_piano_number}/*.jpg"
        jpeg_files = glob.glob(jpeg_files_path)
        for file_path in jpeg_files:
            os.remove(file_path)  
        #cancella i .jpg analizzati
        jpeg_files_path = f"uploads/{mini_piano_number}/analyzed/*.jpg"
        jpeg_files = glob.glob(jpeg_files_path)
        for file_path in jpeg_files:
            os.remove(file_path)              
        
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
async def capture_image(request: Request, mini_piano_number: int, current_position: int):
    try:
        
        print("Server received capture request")
        client_ip = request.client.host
        percorso_cartella = os.path.join(UPLOAD_FOLDER, str(mini_piano_number))

        # Verifica se la cartella del minipiano esiste, altrimenti creala
        if not os.path.exists(percorso_cartella):
            os.makedirs(percorso_cartella)

        # Costruisci il percorso del file utilizzando il numero di minipiano e il timestamp attuale
        timestamp_attuale = int(datetime.timestamp(datetime.now()) * 1000)
        nome_file = f"{timestamp_attuale}.jpg"
        percorso_file = os.path.join(percorso_cartella, nome_file)

        # Effettua la richiesta HTTP per acquisire l'immagine dall'ESP32
        ESP32_URL = f"http://{client_ip}/capture"
        response = requests.get(ESP32_URL)

        # Salva l'immagine nel percorso specificato
        if response.status_code == 200:
            with open(percorso_file, 'wb') as file:
                file.write(response.content)
            imperfection_count, _ = count_imperfections(percorso_file)

            # Scrivi le informazioni nel file di log
            write_to_file(mini_piano_number, current_position, imperfection_count)

            # Invia la risposta in base al valore di imperfection count
            message = "clean" if imperfection_count < 20 else "dirty"
            
            if help_requests!=0:
                message2="SPLIT_WORK:"
                #Occorre mandare il nuovo vettore al robot-quello che ha già percorso
                current_vector=get_vector_from_file("mini_piani_interi.txt",mini_piano_number)
                sub_vector=get_subvector_from_value(current_vector, current_position) #crea un sottovettore delle caselle ancora da pulire
                first_half,second_half=split_vector(sub_vector)
                # Concatenazione di first_half a message2
                message = message+"&"+message2 + " " + " ".join(map(str, first_half))
                help_minipiano=mini_piano_number
                waiting=False
                
              
            
            return {"message": message}

        else:
            return {"error": "Errore durante l'acquisizione dell'immagine"}
    except Exception as e:
        return {"error": f"Errore: {str(e)}"}

@app.get("/uploads/{mini_piano_number}/{file_name}")
async def get_uploaded_file(file_name: str, mini_piano_number: int):
    percorso_file = os.path.join(UPLOAD_FOLDER, str(mini_piano_number), file_name)
    return FileResponse(percorso_file, media_type="image/jpeg")



def update_rewards(mini_piano_number):
    # Step 1: Estrarre il numero di Minipiano
    # Step 2: Leggere il file log.txt
    log_file_path = f"uploads/{mini_piano_number}/log.txt"
    last_rewards = {}
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            
            _, position_str, reward_str = line.split(',')
            position = int(position_str.split(': ')[1])
            reward = int(reward_str.split(': ')[1])
            last_rewards[position] = reward

    # Step 3: Leggere il file c+numeroMinipiano+.txt
    c_file_path = f"uploads/c{mini_piano_number}.txt"
    current_rewards = {}
    with open(c_file_path, 'r') as c_file:
        for line in c_file:
            position, reward = map(int, line.split(': '))
            current_rewards[position] = reward

    # Step 4: Sovrascrivere le ricompense nel vettore corrente
    for position, reward in last_rewards.items():
        current_rewards[position] = reward


    
    # Step 5: Applicare la funzione optimumPath
    P_file_path = f"uploads/P{mini_piano_number}.txt"
    P = read_matrix_from_file(P_file_path)+ 1e-10
    initial_state_index = min(last_rewards.keys())
    final_state_index = max(last_rewards.keys())
    T = 10
    c = np.array(list(current_rewards.values()))
    with open(c_file_path, 'w') as c_file:
        for i, value in enumerate(c, 1):  # Inizia da 1
            c_file.write(f"{i}: {value}\n")
    c = c / np.sum(c)
    c= c+ 1e-10
    dim_c = len(c)
    initial_state = [0] * dim_c
    final_state = [0] * dim_c
    initial_state[initial_state_index - 1] = 1
    final_state[final_state_index - 1] = 1
    final_state = np.array(final_state)+ 1e-10
    initial_state = np.array(initial_state)+ 1e-10
    MaxpostProg_seq_c=optimumPath(P, initial_state, final_state, T, c)
    return MaxpostProg_seq_c

@app.get("/end_transmission")
async def end_transmission(mini_piano_number: str = Query(..., alias="mini_piano_number")):
    # Qui puoi chiamare la funzione per gestire l'evento end_transmission
    
    MaxpostProg_seq_c = update_rewards(mini_piano_number)
    if MaxpostProg_seq_c is not None:
        vector_queue.put((int(mini_piano_number), MaxpostProg_seq_c))
        print_queue(vector_queue)
        return {"message": "End transmission handled successfully"}
    else:
        return {"error": "Unable to calculate MaxpostProg_seq_c"}
    if adv_clean==1:
        num_adv_robot-=1 #decrementa il numero di robot che stanno pulendo in maniera avanzata







if __name__ == "__main__":
    import uvicorn
    # Leggi i vettori dal file di testo al momento dell'avvio dell'applicazione
    c=0    
        # Chiedi all'utente di inserire una stringa
    while c==0:
        input_string = input("Che pulizia vuoi effettuare? Digitare M per Media, A per avanzata: \n")
        # Stampa la stringa inserita dall'utente
        print("Hai scelto:", input_string)
        if input_string=="M":
            read_vectors_from_file("mini_piani.txt")
            c=1
        elif input_string=="A":
            read_vectors_from_file("mini_piani_interi.txt")
            adv_clean=1
            c=1
        else:
            print("Error")
            c=0
    uvicorn.run(app, host="0.0.0.0", port=12345)

