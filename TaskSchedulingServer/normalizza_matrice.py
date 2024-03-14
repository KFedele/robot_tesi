import numpy as np

def normalizza_matrice(b1c):
    b1c = np.nan_to_num(b1c)

    # Calcola la somma lungo l'asse 0
    #sum_b1c = np.sum(b1c, axis=0)+ 1e-10
    sum_b1c = np.sum(b1c, axis=0)+ 1e-10
    sum_b1c = np.nan_to_num(sum_b1c)

    # Calcola l'inversa della somma
    sum_b1c_inverse = 1 / sum_b1c
    sum_b1c_inverse = np.nan_to_num(sum_b1c_inverse)

    # Moltiplica la matrice b1c per la sua inversa
    b1c_normalized = b1c @ sum_b1c_inverse
    b1c_normalized = b1c_normalized / np.sum(b1c_normalized)
    b1c_normalized=b1c_normalized.reshape((len(b1c_normalized), 1))
    b1c=b1c_normalized


    return b1c