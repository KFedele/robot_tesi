import socket

# Configurazioni del server
HOST = '0.0.0.0'
PORT = 12345
FILE_NAME = 'percorsoOttimo.txt'

# Funzione per gestire la connessione del client
def handle_client_connection(client_socket):
    with open(FILE_NAME, 'rb') as file:
        data = file.read()
        client_socket.sendall(data)
        # Invia il messaggio di "fine trasmissione" al client
        client_socket.sendall(b"END")

# Creazione del socket del server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server in ascolto su {HOST}:{PORT}")

while True:
    client_sock, addr = server_socket.accept()
    print(f"Connessione accettata da {addr[0]}:{addr[1]}")
    handle_client_connection(client_sock)
    client_sock.close()
