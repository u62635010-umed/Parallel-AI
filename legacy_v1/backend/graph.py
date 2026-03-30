from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, START, END
from google import genai
from google.genai import types
import os

from dotenv import load_dotenv
load_dotenv()

class AgentState(TypedDict):
    user_input: str
    action: str  # "chat" or "explain"
    main_response: Optional[str]
    selected_point: Optional[int]
    explanation: Optional[str]

# Initialize Gemini 3 Client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
model_id = "gemini-3-flash-preview"

def main_agent(state: AgentState) -> AgentState:
    prompt = """Answer the user query in exactly 5 clear and concise points.
Make sure the points are numbered 1 to 5."""
    
    response = client.models.generate_content(
        model=model_id,
        contents=[prompt, state["user_input"]]
    )
    
    return {"main_response": response.text}

def explainer_agent(state: AgentState) -> AgentState:
    prompt = f"""Given the original question and its answer, explain ONLY point {state['selected_point']} in simple terms with examples.
    
Original Question: {state['user_input']}
Main Answer: {state['main_response']}
"""
    
    response = client.models.generate_content(
        model=model_id,
        config=types.GenerateContentConfig(
            system_instruction="You are a helpful explainer assistant."
        ),
        contents=prompt
    )
    
    return {"explanation": response.text}

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
