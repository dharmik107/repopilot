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
        padding: 0.4rem 0.8rem;
        transition: all 0.3s ease;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(30, 60, 114, 0.4);
    }

    /* Red Delete Button */
    div.stButton > button[kind="secondary"] {
        background: linear-gradient(90deg, #ff4b2b 0%, #ff416c 100%);
    }

    /* Input Fields */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 10px;
    }

    /* Project Cards */
    .project-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }

    .sidebar-header {
        color: #4facfe;
        font-weight: 700;
        letter-spacing: 1px;
        margin-top: 20px;
        font-size: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# State initialization
if 'selected_repo' not in st.session_state:
    st.session_state.selected_repo = None

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.markdown('<h1 class="title-text" style="font-size: 2rem;">RepoPilot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="tagline-text" style="font-size: 0.8rem;">“Navigate any codebase instantly.”</p>', unsafe_allow_html=True)
    
    st.markdown('<h2 class="sidebar-header">🛠️ TECH STACK</h2>', unsafe_allow_html=True)
    st.markdown("""
        <div style="display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 20px;">
            <span style="background: rgba(79, 172, 254, 0.1); color: #4facfe; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; border: 1px solid rgba(79, 172, 254, 0.2);">NeonDB</span>
            <span style="background: rgba(0, 242, 254, 0.1); color: #00f2fe; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; border: 1px solid rgba(0, 242, 254, 0.2);">FastAPI</span>
            <span style="background: rgba(34, 197, 94, 0.1); color: #22c55e; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; border: 1px solid rgba(34, 197, 94, 0.2);">Pinecone</span>
            <span style="background: rgba(168, 85, 247, 0.1); color: #a855f7; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; border: 1px solid rgba(168, 85, 247, 0.2);">LangGraph</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<h2 class="sidebar-header">ADD NEW REPOSITORY</h2>', unsafe_allow_html=True)
    new_repo_url = st.text_input("Repo Link", key="new_repo", placeholder="https://github.com/user/repo")
    if st.button("Index & Add"):
        if new_repo_url:
            with st.spinner("🚀 Analyzing codebase..."):
                try:
                    res = requests.post(f"{API_URL}/load_repo", json={"repo_url": new_repo_url})
                    if res.status_code == 200:
                        st.success("Repository Added!")
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Backend offline: {e}")

    st.markdown('<h2 class="sidebar-header">📂 MY PROJECTS</h2>', unsafe_allow_html=True)
    try:
        projects = requests.get(f"{API_URL}/projects").json()
        if not projects:
            st.info("No projects yet.")
        for p in projects:
            with st.container():
                st.markdown(f"**{p['name']}**")
                cols = st.columns([1, 1])
                if cols[0].button("Select", key=f"sel_{p['id']}"):
                    st.session_state.selected_repo = p['repo_url']
                    st.session_state.messages = [] # Reset chat for new repo
                    st.toast(f"Switched to {p['name']}")
                if cols[1].button("Delete", key=f"del_{p['id']}", type="secondary"):
                    with st.spinner("Deleting..."):
                        requests.delete(f"{API_URL}/projects/{p['id']}")
                        if st.session_state.selected_repo == p['repo_url']:
                            st.session_state.selected_repo = None
                            st.session_state.messages = []
                        st.rerun()
                st.markdown("---")
    except Exception:
        st.error("Failed to load projects.")

# Main Interface
if st.session_state.selected_repo:
    curr_name = st.session_state.selected_repo.split("/")[-1].replace(".git", "")
    st.markdown(f"### Currently Navigating: `{curr_name}`")
    
    # Chat display
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask anything about this codebase..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty() # Create a clean placeholder
            with st.spinner("RepoPilot Agent thinking..."):
                try:
                    res = requests.post(
                        f"{API_URL}/ask", 
                        json={"query": prompt, "repo_url": st.session_state.selected_repo}
                    )
                    if res.status_code == 200:
                        answer = res.json()["answer"]
                        response_placeholder.write(answer) # Output to placeholder
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Error: {e}")
else:
    # Welcome Screen
    st.markdown("""
        <div style="text-align: center; padding: 100px 20px;">
            <h1 style="font-size: 3.5rem; background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Welcome to RepoPilot
            </h1>
            <p style="font-size: 1.5rem; color: #888;">Select a project from the sidebar or add a new one to start navigating.</p>
            <div style="margin-top: 40px; display: flex; justify-content: center; gap: 20px;">
                <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; width: 250px; border: 1px solid rgba(255,255,255,0.1);">
                    <h4 style="color: #4facfe;">Fast Insight</h4>
                    <p style="font-size: 0.9rem; color: #666;">Get answers from large codebases in seconds.</p>
                </div>
                <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; width: 250px; border: 1px solid rgba(255,255,255,0.1);">
                    <h4 style="color: #00f2fe;">Multi-Repo</h4>
                    <p style="font-size: 0.9rem; color: #666;">Switch between projects seamlessly with NeonDB.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
