from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph_tool import get_graph_agent, set_driver, settings
import os
import json
from neo4j import AsyncGraphDatabase
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache

# Setup basic in-memory exact-match cache to improve latency for repeated queries
set_llm_cache(InMemoryCache())

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize Neo4j driver
    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri, 
        auth=(settings.neo4j_user, settings.neo4j_password)
    )
    # Verify connectivity, fail-fast if Neo4j is down
    await driver.verify_connectivity()
    set_driver(driver)
    
    yield
    
    # Shutdown: close driver
    await driver.close()

app = FastAPI(title="Graph RAG Microservices API", lifespan=lifespan)

# Initialize the agent
# Fail-fast if GOOGLE_API_KEY is not set (pydantic-settings handles this, but agent init could fail)
try:
    agent_executor = get_graph_agent()
except Exception as e:
    raise RuntimeError(f"Could not initialize agent. Ensure GOOGLE_API_KEY is set. Error: {e}")

from langchain_core.messages import HumanMessage, AIMessage

class ChatRequest(BaseModel):
    message: str
    chat_history: list[dict] = []

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not agent_executor:
        raise HTTPException(status_code=500, detail="Agent not initialized.")
    
    # Convert dict history to LangChain messages, truncate to last 10 to avoid blowing context window
    formatted_history = []
    for msg in request.chat_history[-10:]:
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
