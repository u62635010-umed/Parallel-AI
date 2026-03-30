import streamlit as st
import os
from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, START, END
from groq import Groq
from dotenv import load_dotenv

# Load local .env for development, Streamlit Cloud uses st.secrets
load_dotenv()

# --- LANGGRAPH LOGIC ---

class AgentState(TypedDict):
    user_input: str
    action: str  # "chat" or "explain"
    main_response: Optional[str]
    selected_point: Optional[int]
    explanation: Optional[str]

# Initialize API Key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        pass

# Fallback: Sidebar input for premium user experience
if not api_key:
    with st.sidebar:
        st.header("🔑 Configuration")
        st.markdown("Please enter your Groq API Key to start exploring.")
        api_key = st.text_input("GROQ_API_KEY", type="password")
        if not api_key:
            st.info("💡 You can get an API key from [Groq Console](https://console.groq.com/).")
            st.stop()

client = Groq(api_key=api_key)
model_id = "llama-3.3-70b-versatile"  # High-performance Groq model

def main_agent(state: AgentState) -> AgentState:
    prompt = """Answer the user query in exactly 5 clear and concise points.
Make sure the points are numbered 1 to 5."""
    
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": state["user_input"]}
        ]
    )
    
    return {"main_response": response.choices[0].message.content}

def explainer_agent(state: AgentState) -> AgentState:
    prompt = f"""Given the original question and its answer, explain ONLY point {state['selected_point']} in simple terms with examples.
    
Original Question: {state['user_input']}
Main Answer: {state['main_response']}
"""
    
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are a helpful explainer assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return {"explanation": response.choices[0].message.content}

def route_action(state: AgentState) -> str:
    if state.get("action") == "explain":
        return "explainer"
    return "main"

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("main", main_agent)
workflow.add_node("explainer", explainer_agent)

workflow.add_conditional_edges(
    START,
    route_action,
    {
        "main": "main",
        "explainer": "explainer"
    }
)
workflow.add_edge("main", END)
workflow.add_edge("explainer", END)

app_graph = workflow.compile()


# --- STREAMLIT UI ---

# Setup Page Configuration
st.set_page_config(
    page_title="Parallel Explainer",
    page_icon="🧠",
    layout="wide",
)

# Custom CSS
st.markdown("""
<style>
    .main-chat-container { padding: 20px; border-radius: 15px; background: rgba(255, 255, 255, 0.05); }
    .explainer-panel { padding: 20px; border-radius: 15px; background: rgba(99, 102, 241, 0.05); height: 100%; border-left: 1px solid rgba(99, 102, 241, 0.2); }
    .stButton>button { border-radius: 10px; width: 100%; }
</style>
""", unsafe_allow_html=True)

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
    <h1 style="font-size: 2.5rem; font-weight: 700; color: #6366f1;">
        🧠 Parallel Explainer
    </h1>
    <p style="font-size: 1.1rem; color: #94a3b8;">
        An agentic system for context-isolated, deep-dive explanations.
    </p>
</div>
""", unsafe_allow_html=True)

# Layout: main chat and side panel
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.markdown('<div class="main-chat-container">', unsafe_allow_html=True)
    st.subheader("💬 Conversation")
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Chat input
    if prompt := st.chat_input("Ask me something complex..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.spinner("🧠 Agent Thinking..."):
            try:
                # Call LangGraph directly
                result = app_graph.invoke({"user_input": prompt, "action": "chat"})
                main_response = result["main_response"]
                
                # Save to state
                st.session_state.main_response = main_response
                st.session_state.messages.append({"role": "assistant", "content": main_response})
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")

    # Point selection buttons
    if st.session_state.main_response:
        st.write("---")
        st.info("Select a point for a deep-dive from the Explainer Agent.")
        
        # Button Grid
        cols = st.columns(5)
        for i in range(1, 6):
            if cols[i-1].button(f"Point {i}", key=f"btn_{i}"):
                st.session_state.selected_point = i
                
                # Fetch explanation via Graph
                with st.spinner(f"🔍 Exploring Point {i}..."):
                    try:
                        latest_user_query = [m["content"] for m in st.session_state.messages if m["role"] == "user"][-1]
                        
                        resp = app_graph.invoke({
                            "user_input": latest_user_query,
                            "main_response": st.session_state.main_response,
                            "selected_point": i,
                            "action": "explain"
                        })
                        st.session_state.explanation = resp["explanation"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Explainer Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="explainer-panel">', unsafe_allow_html=True)
    st.subheader("🎯 Detail Explorer")
    
    if st.session_state.selected_point and st.session_state.explanation:
        st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 12px; padding: 15px;">
            <h4 style="color: #6366f1; margin: 0 0 10px 0;">Point {st.session_state.selected_point} Context</h4>
            <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.5;">{st.session_state.explanation}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Clear Panel", type="secondary"):
            st.session_state.selected_point = None
            st.session_state.explanation = None
            st.rerun()
    else:
        st.info("Choose a point to explore dedicated insights here.")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; padding: 20px; color: #475569; font-size: 0.8rem;">
    Powered by LangGraph & Streamlit Community Cloud
</div>
""", unsafe_allow_html=True)
