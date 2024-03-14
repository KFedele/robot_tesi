from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from queue import Queue

app = FastAPI()

# Crea una coda per i vettori
vector_queue = Queue()

# Aggiungi alcuni vettori alla coda (esempio)
for i in range(1, 6):
    vector_queue.put([i] * 5)

class VectorRequest(BaseModel):
    pass

class VectorResponse(BaseModel):
    vector: list

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
