from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.loader import load_repo
from backend.agents import solve_query
from backend.vector_store import clear_vector_store, delete_repo
from backend.database import get_db, Project

app = FastAPI(title="RepoPilot API")

class RepoRequest(BaseModel):
    repo_url: str

class QueryRequest(BaseModel):
    query: str
    repo_url: str = None

@app.post("/load_repo")
async def load_repository(request: RepoRequest):
    try:
        num_splits = load_repo(request.repo_url)
        return {"message": f"Successfully loaded and indexed {num_splits} code chunks."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects")
async def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return [{"id": p.id, "name": p.name, "repo_url": p.repo_url} for p in projects]

@app.delete("/projects/{project_id}")
async def remove_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Delete from Pinecone
        delete_repo(project.repo_url)
        # Delete from NeonDB
        db.delete(project)
        db.commit()
        return {"message": f"Project {project.name} deleted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(request: QueryRequest):
    try:
        answer = solve_query(request.query, request.repo_url)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear")
async def clear_data():
    try:
        clear_vector_store()
        # Note: This clears ALL vectors, usually for maintenance
        return {"message": "Vector database cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
