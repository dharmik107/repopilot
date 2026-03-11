import streamlit as st
import requests
import time

API_URL = "http://localhost:8000"

st.set_page_config(page_title="RepoPilot", page_icon="🚀", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: white;
    }
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 RepoPilot")
st.subheader("Your Agentic GitHub Repository Assistant")

if 'indexed' not in st.session_state:
    st.session_state.indexed = False

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sidebar for repo loading
with st.sidebar:
    st.header("📂 Repository")
    repo_url = st.text_input("GitHub Repo Link", placeholder="https://github.com/user/repo")
    
    if st.button("Load & Index"):
        if repo_url:
            with st.spinner("Cloning and indexing repository..."):
                try:
                    response = requests.post(f"{API_URL}/load_repo", json={"repo_url": repo_url})
                    if response.status_code == 200:
                        st.success(response.json()["message"])
                        st.session_state.indexed = True
                    else:
                        st.error(f"Error: {response.json()['detail']}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {e}")
        else:
            st.warning("Please enter a repository URL.")

    if st.button("Clear Vector DB & Session"):
        try:
            requests.post(f"{API_URL}/clear")
            st.session_state.indexed = False
            st.session_state.messages = []
            st.success("Data cleared!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Failed to clear: {e}")

# Chat interface
if st.session_state.indexed:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about the repo..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Agent is thinking..."):
                try:
                    response = requests.post(f"{API_URL}/ask", json={"query": prompt})
                    if response.status_code == 200:
                        answer = response.json()["answer"]
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        st.error("Error fetching answer.")
                except Exception as e:
                    st.error(f"Error: {e}")
else:
    st.info("👈 Please load a GitHub repository from the sidebar to start chatting.")
