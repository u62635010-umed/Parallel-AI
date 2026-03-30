from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph import app_graph
import os

app = FastAPI(title="LangGraph Explainer Backend")

# Add CORS Middleware to allow requests from the Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_input: str

class ChatResponse(BaseModel):
    main_response: str

class ExplainRequest(BaseModel):
    user_input: str
    main_response: str
    selected_point: int

class ExplainResponse(BaseModel):
    explanation: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        result = app_graph.invoke({
            "user_input": request.user_input,
            "action": "chat"
        })
        return ChatResponse(main_response=result["main_response"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain", response_model=ExplainResponse)
async def explain_endpoint(request: ExplainRequest):
    try:
        result = app_graph.invoke({
            "user_input": request.user_input,
            "main_response": request.main_response,
            "selected_point": request.selected_point,
            "action": "explain"
        })
        return ExplainResponse(explanation=result["explanation"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
