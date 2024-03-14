
import numpy as np

def retaut_2(N):
    
    
    d=N+1
    
    P = np.zeros((N*N, N*N))
    # Aggiungi una sola riga di zeri
    nuova_riga = np.zeros((1, N*N))
    P = np.vstack((P, nuova_riga))

    # Aggiungi una sola colonna di zeri
    nuova_colonna = np.zeros((N*N + 1, 1))
    P = np.hstack((P, nuova_colonna))
    # Angolo in alto a sinistra OK
    P[1, 1] = 1/3
    P[1, 2] = 1/3
    P[1, N+1] = 1/3

    # Angolo in alto a destra OK
    P[N, N-1] = 1/3
    P[N, N] = 1/3
    P[N, 2*N] = 1/3

    # Angolo in basso a sinistra OK
    P[N*(N-1)+1, N*(N-1)+2] = 1/3
    P[N*(N-1)+1, N*(N-2)+1] = 1/3
    P[N*(N-1)+1, N*(N-1)+1] = 1/3

    # Angolo in basso a destra OK
    P[N*N, N*N] = 1/3
    P[N*N, (N*N)-1] = 1/3
    P[N*N, N*(N-1)] = 1/3

    # Cornice in alto OK
    for i in range(2, N):
        P[i, i-1] = 1/4
        P[i, i] = 1/4
        P[i, i+1] = 1/4
        P[i, N+i] = 1/4

    # Cornice a destra OK
    for i in range(2, N):
        P[i*N, (i-1)*N] = 1/4
        P[i*N, (i*N)-1] = 1/4
        P[i*N, i*N] = 1/4
        P[i*N, (i+1)*N] = 1/4

    # Cornice a sinistra OK
    for i in range(1, N-1):
        P[(N*i)+1, (N*i)+1] = 1/4
        P[(N*i)+1, (N*i)+2] = 1/4
        P[(N*i)+1, (N*(i+1))+1] = 1/4
        P[(N*i)+1, (N*(i-1))+1] = 1/4

    # Cornice in basso OK
    for i in range(1, N-1):
        P[N*N-i, N*N-i] = 1/4
        P[N*N-i, N*(N-1)-i] = 1/4
        P[N*N-i, N*N-i+1] = 1/4
        P[N*N-i, N*N-i-1] = 1/4
        
        

    # Parte centrale
    # Parte centrale
    for i in range(1, N-1):
        for j in range(0,N-2):
            P[N*i+2+j, N*i+2+j] = 1/5
            P[N*i+2+j, N*i+3+j] = 1/5
            P[N*i+2+j, N*i+j+1] = 1/5
            P[N*i+2+j, N*(i-1)+2+j] = 1/5
            P[N*i+2+j, N*(i+1)+2+j] = 1/5

    P=P[1:, 1:]

    return P
    
    
    
