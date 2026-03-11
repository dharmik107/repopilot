import os
import shutil
from git import Repo
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from backend.vector_store import get_vector_store

import stat

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

from backend.database import SessionLocal, Project

from langchain_core.documents import Document

def load_repo(repo_url: str):
    repo_path = "./temp_repo"
    
    # Remove existing temp repo if any
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=remove_readonly)
        
    # Clone the repository
    Repo.clone_from(repo_url, to_path=repo_path)
    
    project_name = repo_url.split("/")[-1].replace(".git", "")
    all_docs = []
    
    # Universal File Handler
    text_extensions = {
        ".py", ".js", ".ts", ".html", ".css", ".md", ".txt", ".json", ".yaml", ".yml", ".xml",
        ".cpp", ".c", ".h", ".hpp", ".cs", ".java", ".go", ".rs", ".rb", ".php", ".sh", ".bat",
        ".sql", ".ipynb", ".r", ".swift", ".kt", ".scala", ".lua", ".pl", ".pm", ".t",
        ".educational", ".doc", ".docx", ".pdf" # educational/doc placeholders (metadata as fallback)
    }
    
    binary_extensions = {".png", ".jpg", ".jpeg", ".svg", ".gif", ".ico", ".pdf", ".zip", ".tar", ".gz", ".exe", ".bin"}

    for root, dirs, files in os.walk(repo_path):
        # Skip .git directory
        if ".git" in dirs:
            dirs.remove(".git")
            
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, repo_path)
            ext = os.path.splitext(file)[-1].lower()
            
            try:
                if ext in text_extensions:
                    # Attempt to load as text/code
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        all_docs.append(Document(
                            page_content=content, 
                            metadata={"source": rel_path, "repo_url": repo_url, "type": "text"}
                        ))
                    except (UnicodeDecodeError, PermissionError):
                        # Fallback to metadata for binary-like text files or permissions
                        all_docs.append(Document(
                            page_content=f"File: {file}\nPath: {rel_path}\nDescription: Asset file in the repository.",
                            metadata={"source": rel_path, "repo_url": repo_url, "type": "metadata"}
                        ))
                else:
                    # Binary or Asset - Metadata Only
                    all_docs.append(Document(
                        page_content=f"Asset: {file}\nPath: {rel_path}\nType: {ext or 'unknown'}\nDescription: Non-text file or asset.",
                        metadata={"source": rel_path, "repo_url": repo_url, "type": "asset"}
                    ))
            except Exception as e:
                print(f"Error indexing {file}: {e}")

    if not all_docs:
        return 0

    # Split documents (using RecursiveCharacterTextSplitter for both code and text)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=128)
    splits = splitter.split_documents(all_docs)
    
    # Index documents into Pinecone
    vector_store = get_vector_store()
    vector_store.add_documents(splits)
    
    # Save to NeonDB
    db = SessionLocal()
    try:
        existing_project = db.query(Project).filter(Project.repo_url == repo_url).first()
        if not existing_project:
            new_project = Project(name=project_name, repo_url=repo_url)
            db.add(new_project)
            db.commit()
    finally:
        db.close()
    
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=remove_readonly)
        
    return len(splits)
