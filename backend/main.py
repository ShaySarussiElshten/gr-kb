from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph_tool import get_graph_agent
import os
import json
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache

# Setup basic in-memory cache to improve latency for repeated queries
set_llm_cache(InMemoryCache())

app = FastAPI(title="Graph RAG Microservices API")

# Initialize the agent
# Note: Requires GOOGLE_API_KEY environment variable
try:
    agent_executor = get_graph_agent()
except Exception as e:
    print(f"Warning: Could not initialize agent. Ensure GOOGLE_API_KEY is set. Error: {e}")
    agent_executor = None

from langchain_core.messages import HumanMessage, AIMessage

class ChatRequest(BaseModel):
    message: str
    chat_history: list[dict] = []

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not agent_executor:
        raise HTTPException(status_code=500, detail="Agent not initialized (missing API key?)")
    
    # Convert dict history to LangChain messages
    formatted_history = []
    for msg in request.chat_history:
        if msg.get("role") == "user":
            formatted_history.append(HumanMessage(content=msg.get("content", "")))
        elif msg.get("role") == "assistant":
            formatted_history.append(AIMessage(content=msg.get("content", "")))
            
    try:
        result = await agent_executor.ainvoke({
            "input": request.message,
            "chat_history": formatted_history
        })
        return ChatResponse(response=result["output"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}
