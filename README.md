# Microservices Architecture Graph RAG

This is a complete prototype of a Graph RAG system that uses a Text-to-Cypher approach to query a synthetic microservices architecture stored in a Neo4j database. 

## Features
- **Synthetic Data Generation**: Simulates a complex architecture with services, databases, message brokers, and teams.
- **Neo4j Graph Database**: Stores the architecture with rich relationships (`CALLS`, `READS_FROM`, `WRITES_TO`, `PUBLISHES_TO`, `MAINTAINS`).
- **Graph RAG Pipeline**: A FastAPI backend using LangChain tool-calling agents. The LLM only loads the graph schema when it actively invokes the Graph Query tool, and the backend handles invalid Cypher queries gracefully.
- **Streamlit Chatbot**: A simple UI to interact with the architecture via natural language.

## Prerequisites
- Docker and Docker Compose
- Python 3.10+
- An OpenAI API Key (for the LLM agent)

## Setup Instructions

1. **Generate the Synthetic Data**:
   ```bash
   python generate_data.py
   ```
   *This creates `data/synthetic_architecture.json`.*

2. **Start the Infrastructure**:
   First, start Neo4j so we can ingest the data:
   ```bash
   docker-compose up -d neo4j
   ```
   *Wait a few moments for Neo4j to fully start.*

3. **Ingest the Graph Data**:
   Install the neo4j Python driver if you haven't already:
   ```bash
   pip install neo4j
   ```
   Then run the ingestion script:
   ```bash
   python ingest_graph.py
   ```
   *You can verify the data by navigating to http://localhost:7474 (Login: neo4j / password).*

4. **Start the Graph RAG API & Chatbot**:
   Set your OpenAI API key as an environment variable and build/start the remaining services:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   docker-compose up --build -d backend frontend
   ```

5. **Interact with the Chatbot**:
   Open your browser and navigate to http://localhost:8501 to use the Streamlit interface.

## Graph Schema Description

The graph represents a microservices environment containing the following nodes and properties:
- `Service` (id, name, language, memory_limit, is_idempotent)
- `Database` (id, name, type, sharding_enabled)
- `MessageBroker` (id, name, type)
- `Team` (id, name, on_call_phone)

And the following relationships:
- `(Service)-[:CALLS {protocol}]->(Service)`
- `(Service)-[:READS_FROM]->(Database)`
- `(Service)-[:WRITES_TO {delivery_semantics}]->(Database)`
- `(Service)-[:PUBLISHES_TO]->(MessageBroker)`
- `(Team)-[:MAINTAINS]->(Service)`

## Text-to-Cypher Graph RAG Approach
This prototype implements an agentic approach to Graph RAG:
1. The FastAPI backend exposes a `Chat` endpoint.
2. It uses a LangChain `tool_calling_agent` initialized with a `query_graph_database` tool.
3. **Lazy Schema Loading**: The agent prompt *does not* contain the full database schema. Only when the agent decides it needs to query the architecture does it invoke the tool.
4. **Tool Execution**: Inside the tool, a dedicated prompt provides the Cypher schema and asks the LLM to convert the user's natural language question into Cypher.
7. **Robust Error Handling**: If the generated Cypher is invalid or the query fails, the tool catches the exception and returns a graceful error string to the agent, allowing the agent to provide a polite fallback response to the user.

## Production-Ready Architecture Decisions
To elevate this project from a working prototype to a robust, production-ready system, the following best practices have been implemented:

1. **Security & Guardrails**:
   - **Cypher Injection Prevention**: A strict Python-level regex validator is embedded inside the database tool, blocking any mutating Cypher operations (`CREATE`, `DELETE`, `MERGE`, `SET`, `DROP`, `REMOVE`, `CALL`).
   - **Topical Guardrails**: The agent's core system prompt explicitly restricts the domain, ensuring the chatbot gracefully refuses off-topic queries (e.g., general knowledge) to prevent Prompt Injection and irrelevant resource usage.
2. **Context Window Optimization (Lazy Loading)**: The complete graph schema is **not** injected into every conversational prompt. It is isolated within the `query_graph_database` tool, meaning it only consumes LLM token context when the agent explicitly decides it needs architectural data.
3. **Resiliency & Performance (Semantic Caching)**: The FastAPI backend implements an `InMemoryCache` for the LLM. Identical or repeated questions are served instantly from the cache, significantly reducing API latency and LLM costs. In a fully scaled environment, this can be seamlessly swapped for a `RedisSemanticCache`.
4. **Conversational Memory**: The backend parses incoming `chat_history` from the frontend and injects it into the LangChain `MessagesPlaceholder`, transforming the stateless RAG into a stateful, conversational AI Agent capable of resolving pronouns and multi-turn context.
5. **Asynchronous Non-Blocking Execution**: The entire backend lifecycle (FastAPI -> LangChain Agent -> Neo4j `AsyncGraphDatabase`) is fully asynchronous (`async`/`await`), allowing the system to handle thousands of concurrent queries without blocking threads.
6. **Configuration & Validation (Fail-Fast)**: System configuration is strictly managed using `pydantic-settings`. Environment variables are validated at startup, guaranteeing a fail-fast boot sequence rather than unexpected runtime crashes.
7. **Automated Evaluation**: The repository includes an `evaluate_rag.py` script that acts as an LLM-as-a-judge against a golden dataset. It automatically scores the system on **Answer Relevance** and **Groundedness**, ensuring consistent quality across model updates.

## Example Questions
Try asking the chatbot these questions:
1. *"Which services will be affected if the Redis database goes down?"*
2. *"Show me the path of a request from the API Gateway to the billing database."*
3. *"Which team maintains the recommendation service and what is their on-call phone number?"*

## Assumptions & Limitations
- **Data Volume**: The synthetic dataset is relatively small for demonstration purposes. In a massive enterprise architecture, the LLM-generated Cypher queries might need further optimization (e.g., using explicit Neo4j Full-Text indexes) to avoid expensive graph traversals.
- **Text-to-Cypher Limitations**: Generating Cypher dynamically via LLM is powerful but can be prone to hallucination. To mitigate this, we rely on a highly rigid `system` prompt inside the `query_graph_database` tool, but complex multi-hop ambiguous questions might occasionally fail to translate perfectly.
- **Stateless Tooling**: While the chatbot interface has conversational memory, the Neo4j database connection itself is stateless per request. We assume that the architecture graph is mostly read-only for the chatbot's purposes. Mutating operations are strictly blocked by our security guardrails.
