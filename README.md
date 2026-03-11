# RepoPilot 🚀

> **“Navigate any codebase instantly.”**

RepoPilot is a premium, agentic RAG (Retrieval-Augmented Generation) system designed to help you explore, understand, and query large GitHub repositories with ease. Built with a state-of-the-art multi-agent workflow, it provides deep insights into code, documentation, and project assets.

---

## 🎬 Demo

[Watch the RepoPilot Demo Here](DEMO_LINK_PLACEHOLDER)

---

## ✨ Key Features

- **🧠 Agentic RAG (LangGraph)**: Orchestrated via a multi-agent system that evaluates search results, refines queries, and ensures accurate answers.
- **📂 Universal Indexing**: Supports all programming languages (Python, JS, Rust, Go, etc.) and gathers metadata for binary assets and project structure.
- **🗂️ Multi-Repo Support**: Persistent project management powered by **NeonDB** (PostgreSQL). Switch between repositories seamlessly.
- **⚡ Performance Optimized**: Fast evaluation cycles and metadata-filtered retrieval using **Pinecone** for low-latency responses.
- **🖼️ Asset Awareness**: Recognizes visual assets, documentation, and niche file types within your codebase.
- **💎 Premium UI**: A sleek, modern dark-themed dashboard built with **Streamlit** featuring glassmorphism and real-time chat.

---

## 🛠️ Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiapi.com/)
- **Database**: [NeonDB](https://neon.tech/) (PostgreSQL), [Pinecone](https://www.pinecone.io/) (Vector Store)
- **AI Framework**: [LangChain](https://www.langchain.com/), [LangGraph](https://langchain-ai.github.io/langgraph/)
- **LLM**: [Groq](https://groq.com/) (Llama-3.1-8B)
- **Embeddings**: [HuggingFace](https://huggingface.co/) (all-mpnet-base-v2)
- **Frontend**: [Streamlit](https://streamlit.io/)

---

## 🚀 Getting Started

### 1. Prerequisites
- [Conda](https://docs.conda.io/en/latest/)
- Python 3.10+

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/dharmik107/repopilot.git
cd RepoPilot
```

### 3. Environment Setup
Create a `.env` file based on `.env.example`:
```env
GROQ_API_KEY=your_key
PINECONE_API_KEY=your_key
PINECONE_INDEX_NAME=repopilotdb
NEON_DATABASE_URL=your_postgres_url
HUGGINGFACEHUB_API_TOKEN=your_token
```

### 4. Run RepoPilot
Simply run the startup batch file:
```bash
start.bat
```
*Alternatively, you can start the backend (`python -m backend.app`) and frontend (`streamlit run frontend/streamlit_app.py`) manually.*

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Developed with ❤️ by [Dharmik107](https://github.com/dharmik107)
