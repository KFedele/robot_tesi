from impFind import highlight_imperfections
from retaut_2 import retaut_2
import os
import numpy as np
from tabulate import tabulate
from optimumPath import optimumPath
from scipy.io import savemat

###############Dalle foto ricava le reward per ogni posizione

image_folder_path = 'C:/Users/katyl/Desktop/Codici_tesi/ConversioneDati/MachineLearning/uploads'
# Specifica il percorso del file di output
output_file_path = 'c1.txt'

# try:
    # os.remove(output_file_path)
    # print(f"Il file {output_file_path} è stato cancellato con successo.")
# except FileNotFoundError:
    # print(f"Il file {output_file_path} non esiste.")
# except PermissionError:
    # print(f"Impossibile cancellare il file {output_file_path}. Assicurati di avere i permessi necessari.")
# except Exception as e:
    # print(f"Si è verificato un errore durante la cancellazione del file {output_file}: {e}")
##Iterate through all images in the folder
# for filename in os.listdir(image_folder_path):
    # if filename.endswith(('.jpg', '.png', '.jpeg')):
        # image_path = os.path.join(image_folder_path, filename)
        # imperfection_count = highlight_imperfections(image_path, output_file_path)
        # print(f"{os.path.basename(image_path)} - Imperfection Level: {imperfection_count}")

# print("Imperfection counts written to", output_file_path)

#################################################

# Carica c1 da un file di testo
with open("c1.txt", "r") as file:
    lines = file.readlines()

# Estrai i valori dopo i ":" e li converte in un vettore
c = [int(line.split(":")[1].strip()) for line in lines]


######ATTENZIONE!!! Qui c1 non è stato ancora riordinato secondo l'ordine di scatto foto. Va prima riordinato.

####Riordinamento vettore C1

# Estrai gli elementi a serpentina
vec=np.arange(1, len(c)+1)

posizioni_desiderate = []
lensqc=len(c)**0.5
lensqc=int(lensqc)
matrice = np.array(vec).reshape((lensqc, lensqc))


for riga in range(lensqc):
    if riga % 2 == 0:
        # Se la riga è pari, aggiungi gli elementi dalla prima all'ultima colonna
        posizioni_desiderate.extend(matrice[riga, :])
    else:
        # Se la riga è dispari, aggiungi gli elementi dalla ultima alla prima colonna
        posizioni_desiderate.extend(matrice[riga, ::-1])

# Crea una lista di tuple contenenti l'elemento e la posizione
elementi_posizioni = list(zip(c, posizioni_desiderate))

# Ordina la lista basandoti sulle posizioni desiderate
elementi_posizioni.sort(key=lambda x: x[1])

# Estrai gli elementi ordinati
c = [elemento[0] for elemento in elementi_posizioni]

########Definizione parametri griglia intera

n_map=lensqc
P = retaut_2(n_map) 
N, M = P.shape
T = 30 #impostare tempo di pulizia


############################################
###Suddivisione dei piani

#Ad ogni minipiano devo associare una matrice miniP (minipiano) ed un vettore mini_c rispettivo

#Dimensioni massime e minime splitting megapiano
n_mini_pari_min=2
n_mini_pari_max=4

n_mini_dispari_min=2
n_mini_dispari_max=4

#campione matrice 
matrice = np.array(vec).reshape((lensqc, lensqc))



n_pari_ok=n_mini_pari_min #si può scegliere anche n_mini_pari_max, per splittare il piano in 4 parti



#########Griglia Npari x Npari

if n_map% 2 == 0:
##########Splitting minimo (2 parti)
    if n_pari_ok==n_mini_pari_min: 
        # Dividi la matrice a metà
               
        #########Metà destra 
        
        num_colonne = matrice.shape[1]
        meta_sinistra = matrice[:, :num_colonne // 2]
        ob_vec_1 = meta_sinistra.flatten()
        P1=P
        c1=c;
        c1 = c1 / np.sum(c1)
        for i in ob_vec_1:
            P1[i-1,:]=0
            P1[:,i-1]=0
            c1[i-1]=0
        #print(tabulate(P1, tablefmt="fancy_grid"))  
        a = (int(n_map/2))+1
        b = N
        initial_state = np.zeros(N)
        initial_state[a-1] = 1
        final_state = np.zeros(N)
        final_state[b-1] = 1 
        
        #Ora si può avviare il path ottimo con P1,c1,initial_state e final_state nuovi

        maxPostProg_seq_c1=optimumPath(P1, initial_state,final_state, T, c1)
        print(maxPostProg_seq_c1)
        
            
        ########Metà sinistra
        P = retaut_2(n_map)
        meta_destra = matrice[:, num_colonne // 2:]
        ob_vec_2 = meta_destra.flatten()
        P2=P;
        c2=c;
        c2 = c2 / np.sum(c2)
        for i in ob_vec_2:
            P2[i-1,:]=0
            P2[:,i-1]=0
            c2[i-1]=0
        #print(tabulate(P2, tablefmt="fancy_grid"))  
        
        a = 1
        b = N-(int(n_map/2))
        initial_state_2 = np.zeros(N)
        initial_state_2[a-1] = 1
        final_state_2 = np.zeros(N)
        final_state_2[b-1] = 1    
        
        maxPostProg_seq_c2=optimumPath(P2, initial_state_2,final_state_2, T, c2)
        print(maxPostProg_seq_c2)
        
    else: 
    ########Splitting massimo (4 parti)
