import streamlit as st
import requests
import time

API_URL = "http://localhost:8000"

st.set_page_config(page_title="RepoPilot", page_icon="🚀", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #050505;
        color: #E0E0E0;
    }

    .main {
        background: linear-gradient(135deg, #050505 0%, #0a0a12 100%);
    }

    /* Glassmorphism for Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(15, 15, 25, 0.7);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Modern Title & Tagline */
    .title-text {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .tagline-text {
        font-size: 1.2rem;
        background: linear-gradient(90deg, #aaaaaa 0%, #ffffff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: -10px;
        margin-bottom: 30px;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        padding: 0.6rem 1rem;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(30, 60, 114, 0.4);
        background: linear-gradient(90deg, #2a5298 0%, #1e3c72 100%);
    }

    /* Input Fields */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 10px;
    }

    /* Chat Styling */
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Realistic Chat Bubbles (Handled via st.chat_message but styled subtly) */
    div[data-testid="stChatMessageContent"] {
        background: transparent !important;
    }

    /* Sidebar headers */
    .sidebar-header {
        color: #4facfe;
        font-weight: 700;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# App Logo and Tagline
st.markdown('<h1 class="title-text">RepoPilot</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline-text">“Navigate any codebase instantly.”</p>', unsafe_allow_html=True)

if 'indexed' not in st.session_state:
    st.session_state.indexed = False

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sidebar for repo loading
with st.sidebar:
    st.markdown('<h2 class="sidebar-header">🛠️ CORE TECH STACK</h2>', unsafe_allow_html=True)
    st.markdown("""
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 25px;">
            <span style="background: rgba(79, 172, 254, 0.15); color: #4facfe; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; border: 1px solid rgba(79, 172, 254, 0.3); font-weight: 600;">FastAPI</span>
            <span style="background: rgba(0, 242, 254, 0.15); color: #00f2fe; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; border: 1px solid rgba(0, 242, 254, 0.3); font-weight: 600;">Streamlit</span>
            <span style="background: rgba(168, 85, 247, 0.15); color: #a855f7; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; border: 1px solid rgba(168, 85, 247, 0.3); font-weight: 600;">LangGraph</span>
            <span style="background: rgba(34, 197, 94, 0.15); color: #22c55e; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; border: 1px solid rgba(34, 197, 94, 0.3); font-weight: 600;">Pinecone</span>
            <span style="background: rgba(245, 158, 11, 0.15); color: #f59e0b; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; border: 1px solid rgba(245, 158, 11, 0.3); font-weight: 600;">Groq</span>
            <span style="background: rgba(236, 72, 153, 0.15); color: #ec4899; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; border: 1px solid rgba(236, 72, 153, 0.3); font-weight: 600;">HuggingFace</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<h2 class="sidebar-header">📂 PROJECT SOURCE</h2>', unsafe_allow_html=True)
    repo_url = st.text_input("GitHub Repo Link", placeholder="https://github.com/user/repo")
    
    col1, col2 = st.columns(2)
    with col1:
        load_btn = st.button("Index Repo")
    with col2:
        clear_btn = st.button("Clear DB")
    
    if load_btn:
        if repo_url:
            with st.spinner("🚀 Analyzing repository..."):
                try:
                    response = requests.post(f"{API_URL}/load_repo", json={"repo_url": repo_url})
                    if response.status_code == 200:
                        st.success("Repository Ready!")
                        st.session_state.indexed = True
                    else:
                        st.error(f"Error: {response.json()['detail']}")
                except Exception as e:
                    st.error(f"Backend Offline: {e}")
        else:
            st.warning("Please enter a link.")

    if clear_btn:
        try:
            requests.post(f"{API_URL}/clear")
            st.session_state.indexed = False
            st.session_state.messages = []
            st.toast("Database Cleared!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Failed to clear: {e}")

# Main Chat Interface
if st.session_state.indexed:
    # Scrollable container for chat
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    # Sticky Chat Input
    if prompt := st.chat_input("Query the codebase..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("RepoPilot Agent thinking..."):
                try:
                    response = requests.post(f"{API_URL}/ask", json={"query": prompt})
                    if response.status_code == 200:
                        answer = response.json()["answer"]
                        st.write(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        st.error("Retrieval failed.")
                except Exception as e:
                    st.error(f"Error: {e}")
else:
    st.markdown("""
        <div style="text-align: center; padding-top: 50px;">
            <h3 style="color: #666;">Get Started</h3>
            <p style="color: #444;">Insert a GitHub link in the sidebar to begin navigating your code.</p>
        </div>
    """, unsafe_allow_html=True)
