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

def load_repo(repo_url: str):
    repo_path = "./temp_repo"
    
    # Remove existing temp repo if any
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=remove_readonly)
        
    # Clone the repository
    Repo.clone_from(repo_url, to_path=repo_path)
    
    # Load documents
    loader = GenericLoader.from_filesystem(
        repo_path,
        glob="**/*",
        suffixes=[".py", ".js", ".ts", ".html", ".css", ".md"],
        parser=LanguageParser()
    )
    docs = loader.load()
    
    # Split documents
    # Using a general splitter for simplicity, though Language-specific splitters can be used
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)
    
    # Index documents into Pinecone
    vector_store = get_vector_store()
    vector_store.add_documents(splits)
    
    # Cleanup local files
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=remove_readonly)
        
    return len(splits)
