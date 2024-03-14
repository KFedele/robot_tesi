import numpy as np
from tabulate import tabulate

def backwardc(P, final_state, T, c):
    # print(f"fin:{final_state} \n")
    b3c = final_state
    b1c = c * b3c.T
    # print(f"b1c:{b1c} Shape: {b1c.shape}\n")
    b1c = b1c / np.sum(b1c)
    b1c=b1c.T
    # print(f"b1c:{b1c} Shape: {b1c.shape}\n")
    Bc = np.column_stack((b1c, b3c))
    # print(f"Bc:{Bc} Shape: {Bc.shape} \n")

    for t in range(1, T):
        b3c = P @ b1c
        b3c = b3c / (np.sum(b3c)+ 1e-10)
        # if t==1:
         # print(f"b3c:{b3c} \n")

        # Supponendo che tu abbia c e b3c
        b1c = c * b3c
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
       
        Bc = np.column_stack((b1c, b3c, Bc))
        # if t==2:
         # print(f"Bc:{Bc} Shape: {Bc.shape} \n")   
         # print(tabulate(Bc, tablefmt="fancy_grid"))         

    return Bc
