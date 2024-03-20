import numpy as np

def maxpostprog(N, T, initial_state, c, P, Bc):
    
    #initial_state=initial_state.reshape((1, len(initial_state)))
    
    f1c = np.array(initial_state)
    #f1c=f1c.flatten()
    c=np.array(c)
    c=c.reshape((len(c),1))
    #print(f"f1c_init: {f1c} \t shape: {f1c.shape}")
    #print(f"c_init: {c} \t shape: {c.shape}")
    MaxpostProg_seq = []
    MaxpostProg_zo = []

    for t in range(T):
        f3c = f1c * c
        f3c = f3c / (np.sum(f3c)+ 1e-10)     
        bb=Bc[:, 2*t]
        bb=bb.reshape((len(bb),1))    
        pc = f3c * bb  # Modificato l'accesso a Bc
        pc = pc / (np.sum(pc)+ 1e-10)
        i = np.argmax(pc)
        v = np.zeros(N)
        v[i] = 1      
        f1c = P.T @ v
        f1c = f1c / (np.sum(f1c)+ 1e-10)
        f1c=f1c.reshape((len(f1c),1)) 
        
        MaxpostProg_seq.append(i+1)
        MaxpostProg_zo.append(v)

    return MaxpostProg_seq, MaxpostProg_zo
