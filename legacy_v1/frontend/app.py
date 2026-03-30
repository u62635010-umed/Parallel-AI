import streamlit as st
import os
import requests

# Setup Page Configuration
st.set_page_config(
    page_title="LangGraph Premium Explainer",
    page_icon="🧠",
    layout="wide",
)

# Backend Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Custom CSS Injection
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load layout styling
current_dir = os.path.dirname(os.path.abspath(__file__))
local_css(os.path.join(current_dir, "style.css"))

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "main_response" not in st.session_state:
    st.session_state.main_response = None
if "selected_point" not in st.session_state:
    st.session_state.selected_point = None
if "explanation" not in st.session_state:
    st.session_state.explanation = None

# Header Section
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="font-size: 3rem; font-weight: 700; background: -webkit-linear-gradient(#6366f1, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🧠 LangGraph Parallel Explainer
    </h1>
    <p style="font-size: 1.2rem; color: #94a3b8; max-width: 700px; margin: 0 auto;">
        An agentic system providing concise, parallelized explanations for complex topics.
    </p>
</div>
""", unsafe_allow_html=True)

# Layout: main chat and side panel
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.markdown('<div class="main-chat-container">', unsafe_allow_html=True)
    st.subheader("💬 Main Conversation")
    
    # Display chat history with custom style
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Chat input
    if prompt := st.chat_input("Ask me anything about complex systems..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.spinner("🧠 Calling API (Main Agent)..."):
            try:
                # Use FastAPI Backend
                response = requests.post(f"{BACKEND_URL}/chat", json={"user_input": prompt})
                response.raise_for_status()
                data = response.json()
                main_response = data["main_response"]
                
                # Save to state
                st.session_state.main_response = main_response
                st.session_state.messages.append({"role": "assistant", "content": main_response})
                
                with st.chat_message("assistant"):
                    st.markdown(main_response)
            except Exception as e:
                st.error(f"❌ API Error: {e}. Is the FastAPI server running?")

    # Point selection buttons
    if st.session_state.main_response:
        st.write("---")
        st.write("### ✨ Perspective Selection")
        st.info("The Main Agent has provided 5 key points. Select one for a context-isolated, deep-dive explanation from the Explainer Agent.")
        
        # Modern Button Grid
        cols = st.columns(5)
        for i in range(1, 6):
            if cols[i-1].button(f"Dive into Point {i}", key=f"btn_{i}"):
                st.session_state.selected_point = i
                
                # Fetch explanation via API
                with st.spinner(f"🔍 Fetching Detail via API for Point {i}..."):
                    try:
                        latest_user_query = [m["content"] for m in st.session_state.messages if m["role"] == "user"][-1]
                        
                        resp = requests.post(f"{BACKEND_URL}/explain", json={
                            "user_input": latest_user_query,
                            "main_response": st.session_state.main_response,
                            "selected_point": i
                        })
                        resp.raise_for_status()
                        st.session_state.explanation = resp.json()["explanation"]
                    except Exception as e:
                        st.error(f"❌ Explainer API Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="explainer-panel">', unsafe_allow_html=True)
    st.subheader("🎯 Detail Explorer")
    
    if st.session_state.selected_point and st.session_state.explanation:
        # Glass card for explanation
        st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 15px; padding: 20px; margin-bottom: 20px;">
            <h4 style="color: #6366f1; margin-top: 0;">Point {st.session_state.selected_point} Deep Dive</h4>
            <p style="color: #cbd5e1; font-size: 1rem; line-height: 1.6;">{st.session_state.explanation}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Clear Explorer", type="secondary"):
            st.session_state.selected_point = None
            st.session_state.explanation = None
            st.rerun()
    else:
        st.warning("No detail selected.")
        st.markdown("""
        <div style="color: #94a3b8; font-size: 0.9rem;">
            Click one of the "Dive" buttons in the main chat to trigger the <b>Explainer Agent</b>. 
            This agent operates independently of the main conversation flow to provide specialized insights.
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; padding: 40px; color: #475569; font-size: 0.8rem;">
    Powered by LangGraph & Gemini 3 • Premium Streamlit Architecture
</div>
""", unsafe_allow_html=True)
