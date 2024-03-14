import numpy as np

def forwardc(P, initial_state, T, c):
    f1c = initial_state
    f3c = f1c * c
    # print(f"f3c_in: {f3c} \t Shape: {f3c.shape}")
    #normalizzazione
    f3c = np.nan_to_num(f3c)
    sum_f3c = np.sum(f3c, axis=0)+ 1e-10
    sum_f3c = np.nan_to_num(sum_f3c)
    # Calcola l'inversa della somma
    sum_f3c_inverse = 1 / sum_f3c
    sum_f3c_inverse = np.nan_to_num(sum_f3c_inverse)    
    # Moltiplica la matrice b1c per la sua inversa
    f3c_normalized = f3c @ sum_f3c_inverse
    f3c_normalized = f3c_normalized / np.sum(f3c_normalized)
    f3c_normalized=f3c_normalized.reshape((len(f3c_normalized), 1))
    f3c=f3c_normalized    

    Fc = np.column_stack((f1c, f3c))  # Modificato per salvare entrambe le colonne
    
    # print(f"Fc_in: {Fc} \t Shape: {Fc.shape}") #Fin qui tutto ok
    
    
    for t in range(1, T):
        f1c = P.T @ f3c
        f1c = f1c / (np.sum(f1c)+ 1e-10) #OK
        f3c = f1c * c    
        f3c = np.nan_to_num(f3c)
        sum_f3c = np.sum(f3c, axis=0)+ 1e-10
        sum_f3c = np.nan_to_num(sum_f3c)
        # Calcola l'inversa della somma
        sum_f3c_inverse = 1 / sum_f3c
        sum_f3c_inverse = np.nan_to_num(sum_f3c_inverse)    
        # Moltiplica la matrice b1c per la sua inversa
        f3c_normalized = f3c @ sum_f3c_inverse
        f3c_normalized = f3c_normalized / np.sum(f3c_normalized)
        f3c_normalized=f3c_normalized.reshape((len(f3c_normalized), 1))
        f3c=f3c_normalized    
        Fc = np.column_stack((Fc, f1c, f3c))  # Modificato per salvare entrambe le colonne

    return Fc
