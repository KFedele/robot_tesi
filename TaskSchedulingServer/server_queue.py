from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from queue import Queue

app = FastAPI()

# Crea una coda per i vettori
vector_queue = Queue()

class VectorRequest(BaseModel):
    pass

class VectorResponse(BaseModel):
    vector: list

def read_vectors_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        vector = []
        for line in lines:
            if line.startswith("Vettore"):
                if vector:
                    vector_queue.put(vector)
                    vector = []
            else:
                vector.extend(map(int, line.strip().split()))
        if vector:
            vector_queue.put(vector)

# Leggi i vettori dal file di testo al momento dell'avvio dell'applicazione
read_vectors_from_file("mini_piani.txt")

@app.post("/add_vector")
async def add_vector(vector: VectorRequest):
    vector_queue.put(vector.vector)
    return {"message": "Vector added successfully"}

@app.get("/get_vector")
async def get_vector():
    if vector_queue.empty():
        raise HTTPException(status_code=404, detail="No vectors available")
    else:
        return {"vector": vector_queue.get()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
