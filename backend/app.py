from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.loader import load_repo
from backend.agents import solve_query
from backend.vector_store import clear_vector_store

app = FastAPI(title="RepoPilot API")

class RepoRequest(BaseModel):
    repo_url: str

class QueryRequest(BaseModel):
    query: str

@app.post("/load_repo")
async def load_repository(request: RepoRequest):
    try:
        num_splits = load_repo(request.repo_url)
        return {"message": f"Successfully loaded and indexed {num_splits} code chunks."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(request: QueryRequest):
    try:
        answer = solve_query(request.query)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear")
async def clear_data():
    try:
        clear_vector_store()
        return {"message": "Vector database cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
