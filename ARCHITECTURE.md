# 🏗️ RepoPilot Architecture

RepoPilot is built on a modular, agentic RAG architecture designed for multi-repository awareness and universal file indexing.

---

## 🛰️ System Overview

The system consists of three primary layers:
1.  **Frontend**: Streamlit-based dashboard for repo management and interactive chat.
2.  **Backend**: FastAPI server orchestrating data ingestion and agentic workflows.
3.  **Storage**: 
    *   **NeonDB (PostgreSQL)**: Stores project metadata and repository links.
    *   **Pinecone**: High-performance vector store for code and asset embeddings.

```mermaid
graph TD
    User((User)) -->|Interacts| Streamlit[Streamlit Frontend]
    Streamlit -->|API Requests| FastAPI[FastAPI Backend]
    
    subgraph "Ingestion Engine"
        FastAPI -->|Load Repo| Loader[Universal Loader]
        Loader -->|Clones| Git[GitHub]
        Loader -->|Parses & Indexes| Pinecone[(Pinecone Vector DB)]
        Loader -->|Saves Metadata| Neon[(NeonDB PostgreSQL)]
    end
    
    subgraph "Agentic RAG (LangGraph)"
        FastAPI -->|Query| LangGraph[LangGraph Orchestrator]
        LangGraph -->|Search| Pinecone
        LangGraph -->|LLM Reasoning| Groq[Groq Llama-3.1]
    end
```

---

## 🔄 Core Workflows

### 1. Repository Indexing (Universal Loader)
RepoPilot uses a **Universal File Handler** to ensure no data is left behind:
- **Text/Code**: Files in any language are read, parsed using a language-aware approach, and split into chunks.
- **Assets/Binaries**: Images, PDFs, and binaries are indexed via **Metadata Documents** (Path, Filename, Size), allowing the agent to "see" the project structure even for non-text files.

```mermaid
sequenceDiagram
    participant U as User
    participant B as Backend
    participant G as GitHub
    participant P as Pinecone
    participant N as NeonDB
    
    U->>B: Submit Repo URL
    B->>G: Clone Repository
    B->>B: Universal File Detection
    loop For Every File
        alt is Text/Code
            B->>B: Chunk Content
        else is Binary/Asset
            B->>B: Extract Metadata
        end
    end
    B->>P: Bulk Index Vectors + repo_url metadata
    B->>N: Save Project Record
    B-->>U: Indexing Complete
```

### 2. Agentic RAG Flow (LangGraph)
Queries are processed through a cyclic graph of agents to maximize accuracy:
- **Retrieval Agent**: Fetch context snippets filtered strictly by the active `repo_url`.
- **Fast Evaluator**: Checks if retrieved context is sufficient.
- **Query Refiner**: If retrieval fails, rephrases the query for high-level project metadata.
- **Response Agent**: Synthesizes the final answer using multi-modal context.

```mermaid
graph LR
    Start((Query)) --> Retrieval[Retrieval Agent]
    Retrieval --> Evaluator{Fast Evaluator}
    Evaluator -- NO --> Refiner[Query Refiner]
    Refiner --> Retrieval
    Evaluator -- YES --> Response[Response Agent]
    Response --> End((Final Answer))
```

---

## 📊 Data Storage Schema

### NeonDB (PostgreSQL)
- **Table**: `projects`
  - `id`: Primary Key
  - `name`: Repository Name
  - `repo_url`: Unique GitHub URL
  - `description`: Optional project info

### Pinecone (Vector Store)
- **Index Name**: `repopilotdb`
- **Metadata Fields**:
  - `source`: Relative file path
  - `repo_url`: Used for strict query isolation
  - `type`: `text`, `metadata`, or `asset`

---
*Architected for speed, accuracy, and universal codebase support.*
