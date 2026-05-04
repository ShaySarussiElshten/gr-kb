import os
import json
import re
from typing import Any

from pydantic_settings import BaseSettings
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from neo4j import AsyncGraphDatabase

class Settings(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    google_api_key: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# We provide the schema to the tool explicitly so it only loads when the tool is called
GRAPH_SCHEMA = """
Node properties:
- Service {id: STRING, name: STRING, language: STRING, memory_limit: STRING, is_idempotent: BOOLEAN}
- Database {id: STRING, name: STRING, type: STRING, sharding_enabled: BOOLEAN}
- MessageBroker {id: STRING, name: STRING, type: STRING}
- Team {id: STRING, name: STRING, on_call_phone: STRING}

Relationship properties:
- (Service)-[:CALLS {protocol: STRING}]->(Service)
- (Service)-[:READS_FROM]->(Database)
- (Service)-[:WRITES_TO {delivery_semantics: STRING}]->(Database)
- (Service)-[:PUBLISHES_TO]->(MessageBroker)
- (Team)-[:MAINTAINS]->(Service)
"""

@tool
async def query_graph_database(question: str) -> str:
    """
    Use this tool to answer questions about the microservices architecture, 
    services, databases, message brokers, teams, and their relationships.
    You must provide the user's original question as input.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    cypher_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Neo4j Cypher developer. Convert the user's question into a Cypher query based on the following schema:\n{schema}\n\n"
                   "IMPORTANT RULES:\n"
                   "- When filtering by name or type, use case-insensitive matching (e.g., toLower(d.name) CONTAINS 'redis' OR toLower(d.type) CONTAINS 'redis').\n"
                   "- The user might not provide the exact exact string, so be flexible.\n"
                   "- Return ONLY the valid Cypher query without any markdown formatting or explanations."),
        ("user", "{question}")
    ])
    
    cypher_chain = cypher_prompt | llm
    
    try:
        cypher_query_msg = await cypher_chain.ainvoke({"schema": GRAPH_SCHEMA, "question": question})
        cypher_query = str(cypher_query_msg.content).strip()
        
        # Remove any potential markdown block backticks if the LLM hallucinated them
        if cypher_query.startswith("```cypher"):
            cypher_query = cypher_query[9:].strip()
        if cypher_query.startswith("```"):
            cypher_query = cypher_query[3:].strip()
        if cypher_query.endswith("```"):
            cypher_query = cypher_query[:-3].strip()
            
        print(f"Generated Cypher Query:\n{cypher_query}")
        
        # Cypher Injection Prevention (Security Guardrail)
        forbidden_keywords = [r'\bCREATE\b', r'\bDELETE\b', r'\bMERGE\b', r'\bSET\b', r'\bREMOVE\b', r'\bDROP\b', r'\bCALL\b']
        for keyword in forbidden_keywords:
            if re.search(keyword, cypher_query, re.IGNORECASE):
                return f"Query blocked due to security guardrails. Found restricted keyword matching {keyword}."
        
        # Execute query asynchronously
        auth = (settings.neo4j_user, settings.neo4j_password)
        async with AsyncGraphDatabase.driver(settings.neo4j_uri, auth=auth) as driver:
            records, summary, keys = await driver.execute_query(cypher_query, database_="neo4j")
            
            if not records:
                return "The query was successful but returned no results."
            
            # Convert records to list of dicts for easy reading
            results = []
            for record in records:
                results.append(record.data())
            
            return json.dumps(results, indent=2)
            
    except Exception as e:
        # Robust error handling
        return f"Failed to execute graph query. Error: {str(e)}. Please try rephrasing the question or tell the user the query failed gracefully."

from langchain_core.prompts import MessagesPlaceholder

def get_graph_agent() -> AgentExecutor:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    tools = [query_graph_database]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a highly secure AI architect assistant that ONLY answers questions about the company's microservices architecture. "
                   "If the user asks a question that is NOT related to software architecture, microservices, databases, message brokers, technical teams, or their on-call phone numbers, "
                   "you MUST refuse to answer gracefully and remind the user of your strict domain. Do NOT call the database for off-topic questions (like recipes, general knowledge, etc).\n\n"
                   "For relevant architecture questions, use the `query_graph_database` tool. "
                   "If the tool returns an error, apologize and explain that you couldn't retrieve the information. "
                   "Do not make up answers about the architecture if the tool does not provide them."),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor
