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

def load_repo(repo_url: str):
    repo_path = "./temp_repo"
    
    # Speed Optimization: Redundant DB init moved to app startup
    
    # Remove existing temp repo if any
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=remove_readonly)
        
    # Clone the repository
    Repo.clone_from(repo_url, to_path=repo_path)
    
    project_name = repo_url.split("/")[-1].replace(".git", "")
    
    # Load code/text documents
    loader = GenericLoader.from_filesystem(
        repo_path,
        glob="**/*",
        suffixes=[".py", ".js", ".ts", ".html", ".css", ".md", ".txt"],
        parser=LanguageParser()
    )
    docs = loader.load()
    
    # Handle Image Metadata Indexing
    image_extensions = (".png", ".jpg", ".jpeg", ".svg", ".gif", ".ico")
    image_docs = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.lower().endswith(image_extensions):
                rel_path = os.path.relpath(os.path.join(root, file), repo_path)
                doc_content = f"Image File: {file}\nPath: {rel_path}\nDirectory: {os.path.basename(root)}"
                from langchain_core.documents import Document
                image_docs.append(Document(page_content=doc_content, metadata={"source": rel_path, "type": "image"}))
    
    docs.extend(image_docs)

    # Tag all docs with repo_url for filtering
    for doc in docs:
        doc.metadata["repo_url"] = repo_url

    # Split documents
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)
    
    # Index documents into Pinecone
    vector_store = get_vector_store()
    vector_store.add_documents(splits)
    
    # Save to NeonDB
    db = SessionLocal()
    try:
        # Check if exists
        existing_project = db.query(Project).filter(Project.repo_url == repo_url).first()
        if not existing_project:
            new_project = Project(name=project_name, repo_url=repo_url)
            db.add(new_project)
            db.commit()
    finally:
        db.close()
    
    # Cleanup local files
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=remove_readonly)
        
    return len(splits)
