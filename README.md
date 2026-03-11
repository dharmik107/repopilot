# 🚀 RepoPilot
> **Navigate any codebase instantly.** 

[![RepoPilot Demo](https://img.shields.io/badge/Watch-Project%20Demo-blue?style=for-the-badge&logo=linkedin)](DEMO_LINK_PLACEHOLDER)

RepoPilot is an intelligent, agentic RAG system built to explore and query large GitHub repositories with ease. Powered by **LangGraph**, **FastAPI**, and **Streamlit**, RepoPilot uses multi-agent workflows to intelligently index, evaluate, and navigate complex codebases, assets, and documentation.

---

## ✨ Core Features

* **Universal Repository Indexing**
  * Effortlessly index repositories in ANY programming language (Python, JS, C++, Rust, Zig, etc.). RepoPilot handles code, documentation, and educational data seamlessly.
* **Persistent Multi-Repo Management**
  * All projects are stored and managed through **NeonDB (PostgreSQL)**. Access your entire catalog of indexed codebases from the dashboard and switch between them instantly.
* **Agentic RAG Architecture**
  * Built on **LangGraph**, the system employs a multi-agent logic that refines queries, evaluates context snippets, and ensures the highest accuracy in navigating your code.
* **Asset & Metadata Awareness**
  * Beyond code, RepoPilot recognizes visual assets (PNG, JPG, SVG) and non-text files through metadata indexing, giving you a holistic view of your project.
* **Premium UI**
  * Modern, dark-themed Streamlit interface with glassmorphism effects and an intuitive project selection sidebar.

---

## 🛠️ Tech Stack

* **Frontend**: Streamlit
* **Backend**: FastAPI 
* **Database**: Neon (PostgreSQL), Pinecone (Vector Store)
* **AI Orchestration**: LangGraph, LangChain
* **LLM Provider**: Groq (Llama-3.1-8B)
* **Embeddings**: HuggingFace (all-mpnet-base-v2)

---

## 🚀 Quick Setup & Installation

### 1. Prerequisites
Ensure you have Python 3.10+ and Conda installed.

### 2. Environment Variables
Create a `.env` file in the root directory and add the following keys:
```env
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=repopilotdb
NEON_DATABASE_URL="postgresql://username:password@your-neon-db-url/neondb"
HUGGINGFACEHUB_API_TOKEN=your_token
```

### 3. Install Dependencies
Install all required libraries via the provided requirements file:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
You can instantly spin up both the FastAPI backend server and the Streamlit frontend UI simultaneously using the included batch file:
```bash
start.bat
```
*(The backend will run on `http://127.0.0.1:8000` and the UI will open at `localhost`)*

---
*Built to accelerate the future of codebase navigation.*
