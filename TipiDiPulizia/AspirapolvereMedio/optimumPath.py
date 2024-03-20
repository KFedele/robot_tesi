import numpy as np
from backwardc import backwardc
from forwardc import forwardc
from maxpostprog import maxpostprog

def optimumPath(P, initial_state,final_state, T, c):
    N, M = P.shape
    c = np.array(c)  
    final_state=final_state.reshape((len(final_state), 1))
    Bc1 = np.array(backwardc(P, final_state, T, c))
    Bc1 = np.vstack(Bc1)   
    initial_state=initial_state.reshape((len(initial_state), 1))
    Fc1 = np.array(forwardc(P, initial_state, T, c))
    Postc1 = Fc1 * Bc1
    column_sums = np.sum(Postc1, axis=0)
    diago=np.diag(column_sums)
    Postc1= Postc1 @ np.linalg.inv(diago)
    MaxpostProg_seqc1, MaxpostProg_zoc1 = maxpostprog(N, T, initial_state, c, P, Bc1)
    
    return MaxpostProg_seqc1