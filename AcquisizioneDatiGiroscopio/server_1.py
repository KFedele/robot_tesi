import socket
import time
from datetime import datetime

# Configurazioni del server
HOST = '0.0.0.0'
PORT = 12345

# Nome del file per salvare i dati
FILE_NAME = 'dati_giroscopio.txt'

# Funzione per estrarre i dati relativi al giroscopio
def extract_gyroscope_data(data):
    # Cerca la parte del messaggio contenente i dati del giroscopio
    start_index = data.find("a/g:")
    if start_index != -1:
        # Trova la fine della riga contenente i dati del giroscopio
        end_index = data.find("\n", start_index)
        if end_index != -1:
            # Estrae i dati del giroscopio dalla riga
            gyroscope_data = data[start_index:end_index]
            return gyroscope_data
    return None

# Funzione per gestire la connessione del client
def handle_client_connection(client_socket):
    with open(FILE_NAME, 'w') as file:  # Usa 'w' per sovrascrivere il file
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            decoded_data = data.decode('utf-8')
            
            # Estrai i dati relativi al giroscopio dal messaggio
            gyroscope_data = extract_gyroscope_data(decoded_data)
            
            if gyroscope_data:
                #timestamp_ms = int(time.time() * 1000)
                formatted_time=datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                formatted_data = f"{formatted_time}, {gyroscope_data}"
                formatted_data = formatted_data.replace(", a/g:", "")
                print(formatted_data)
                file.write(formatted_data + '\n')


# Creazione del socket del server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server in ascolto su {HOST}:{PORT}")

while True:
    client_sock, addr = server_socket.accept()
    print(f"Connessione accettata da {addr[0]}:{addr[1]}")
    handle_client_connection(client_sock)
