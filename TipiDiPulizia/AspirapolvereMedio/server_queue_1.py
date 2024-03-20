from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
import os
import requests
from optimumPath import optimumPath

from impFindSingolo import count_imperfections

app = FastAPI()

UPLOAD_FOLDER = "C:/Users/katyl/Desktop/Codici_tesi/MangiaPolvere/AspirapolvereMedio/uploads"

def write_to_file(mini_piano_number: int, current_position: int, imperfection_count: int):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = os.path.join(UPLOAD_FOLDER, str(mini_piano_number), "log.txt")
    with open(file_path, "a") as file:
        file.write(f"{current_time}, Position: {current_position}, Reward: {imperfection_count}\n")

def print_queue(queue):
    print("Queue contents:")
    for item in queue:
        print(item)

class VectorRequest(BaseModel):
    pass

class VectorResponse(BaseModel):
    vector: list

def read_vectors_from_file(filename):
    if not os.path.exists(filename):
        print(f"File '{filename}' not found.")
        return

    with open(filename, 'r') as file:
        mini_piano_number = None
        vector = []

        for line in file:
            line = line.strip()

            if line.startswith("Mini-piano"):
                if mini_piano_number is not None and vector:
                    vector_queue.append((mini_piano_number, vector))
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
            vector_queue.append((mini_piano_number, vector))
            print(f"Added vector for mini-piano {mini_piano_number}: {vector}")

@app.get("/queue")
async def get_queue():
    return vector_queue

@app.post("/add_vector")
async def add_vector(vector: VectorRequest):
    vector_queue.append(vector.vector)
    return {"message": "Vector added successfully"}

@app.get("/get_vector")
async def get_vector():
    if not vector_queue:
        raise HTTPException(status_code=404, detail="No vectors available")
    else:
        return vector_queue.pop(0)

def acquisisci_immagine_da_esp32(client_ip: str):
    try:
        ESP32_URL = f"http://{client_ip}/capture"
        response = requests.get(ESP32_URL)
        if response.status_code == 200:
            timestamp_attuale = int(datetime.timestamp(datetime.now()) * 1000)
            nome_file = f"{timestamp_attuale}.jpg"
            percorso_file = os.path.join(UPLOAD_FOLDER, nome_file)
            with open(percorso_file, 'wb') as file:
                file.write(response.content)
            return percorso_file
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Errore durante l'acquisizione dell'immagine: {str(e)}")
        return None

@app.get("/capture")
async def capture_image(request: Request, mini_piano_number: int, current_position: int):
    try:
        print("Server received capture request")
        client_ip = request.client.host
        percorso_cartella = os.path.join(UPLOAD_FOLDER, str(mini_piano_number))
        if not os.path.exists(percorso_cartella):
            os.makedirs(percorso_cartella)
        timestamp_attuale = int(datetime.timestamp(datetime.now()) * 1000)
        nome_file = f"{timestamp_attuale}.jpg"
        percorso_file = os.path.join(percorso_cartella, nome_file)
        ESP32_URL = f"http://{client_ip}/capture"
        response = requests.get(ESP32_URL)
        if response.status_code == 200:
            with open(percorso_file, 'wb') as file:
                file.write(response.content)
            imperfection_count, _ = count_imperfections(percorso_file)
            write_to_file(mini_piano_number, current_position, imperfection_count)
            message = "clean" if imperfection_count < 20 else "dirty"
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
    log_file_path = f"/uploads/{mini_piano_number}/log.txt"
    last_rewards = {}
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            _, _, position_str, _, reward_str = line.split(',')
            position = int(position_str.split(': ')[1])
            reward = int(reward_str.split(': ')[1])
            last_rewards[position] = reward

    c_file_path = f"/uploads/c{mini_piano_number}.txt"
    current_rewards = {}
    with open(c_file_path, 'r') as c_file:
        for line in c_file:
            position, reward = map(int, line.split(': '))
            current_rewards[position] = reward

    for position, reward in last_rewards.items():
        current_rewards[position] = reward

    P_file_path = f"/uploads/P{mini_piano_number}.txt"
    initial_state_index = min(last_rewards.keys())
    final_state_index = max(last_rewards.keys())
    T = 10
    c = list(current_rewards.values())
    dim_c = len(c)
    initial_state = [0] * dim_c
    final_state = [0] * dim_c
    initial_state[initial_state_index - 1] = 1
    initial_state[final_state_index - 1] = 1
    MaxpostProg_seq_c = optimumPath(P_file_path, initial_state, final_state, T, c)
    return MaxpostProg_seq_c

@app.get("/end_transmission")
async def end_transmission(mini_piano_number: str):
    if os.path.exists(f"/uploads/{mini_piano_number}/log.txt"):
        MaxpostProg_seq_c = update_rewards(mini_piano_number)
        vector_queue.append((mini_piano_number, MaxpostProg_seq_c))
        print_queue(vector_queue)
        return {"message": "End transmission handled successfully"}
    else:
        raise HTTPException(status_code=404, detail="Log file not found for the specified mini_piano_number")

if __name__ == "__main__":
    import uvicorn
    read_vectors_from_file("mini_piani.txt")
    uvicorn.run(app, host="0.0.0.0", port=12345)
