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
                # Create a pseudo-document for the image
                doc_content = f"Image File: {file}\nPath: {rel_path}\nDirectory: {os.path.basename(root)}\nDescription: Visual asset in the repository."
                from langchain_core.documents import Document
                image_docs.append(Document(page_content=doc_content, metadata={"source": rel_path, "type": "image"}))
    
    docs.extend(image_docs)

    # Split documents
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)
    
    # Index documents into Pinecone
    vector_store = get_vector_store()
    vector_store.add_documents(splits)
    
    # Cleanup local files
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=remove_readonly)
        
    return len(splits)
