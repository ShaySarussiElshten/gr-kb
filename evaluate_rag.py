import os
import requests
import json
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Golden Dataset: (Question, Expected Keywords/Facts)
GOLDEN_DATASET = [
    {
        "question": "List all databases with sharding enabled.",
        "expected": ["billing-db", "inventory-db"]
    },
    {
        "question": "Which language is the inventory-service written in?",
        "expected": ["Node.js"]
    },
    {
        "question": "What is the memory limit of the user-service?",
        "expected": ["1GB"]
    },
    {
        "question": "List all services that communicate via gRPC.",
        "expected": ["api-gateway", "user-service", "recommendation-service", "billing-service", "notification-service"]
    },
    {
        "question": "Which services are idempotent?",
        "expected": ["api-gateway", "billing-service", "recommendation-service", "notification-service"]
    }
]

def query_system(question: str) -> str:
    url = "http://localhost:8005/chat"
    try:
        response = requests.post(url, json={"message": question}, timeout=60)
        if response.status_code == 200:
            return response.json().get("response", "No response")
        return f"Error {response.status_code}"
    except Exception as e:
        return f"Exception: {str(e)}"

def evaluate_responses():
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    eval_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI evaluator. Your job is to evaluate the quality of a RAG system's response.\n"
                   "Evaluate the response based on two criteria on a scale of 0 to 1:\n"
                   "1. Answer Relevance: Does the generated response directly answer the user's question?\n"
                   "2. Groundedness: Does the generated response correctly include the Expected Facts without hallucinating additional false information?\n"
                   "\n"
                   "Respond strictly in the following JSON format:\n"
                   "{{\n"
                   '  "relevance_score": 1.0,\n'
                   '  "groundedness_score": 1.0,\n'
                   '  "reasoning": "brief explanation"\n'
                   "}}"
         ),
        ("user", "Question: {question}\nExpected Facts: {expected}\nGenerated Response: {response}")
    ])
    
    eval_chain = eval_prompt | llm
    
    print("Starting Automated LLM-as-a-judge Evaluation...\n")
    
    results = []
    
    for item in GOLDEN_DATASET:
        q = item["question"]
        print(f"Testing Q: {q}")
        
        # Get system response
        sys_resp = query_system(q)
        print(f"System Response: {sys_resp}")
        
        if "Error" in sys_resp or "Exception" in sys_resp:
            print(f"Skipping evaluation due to system error.\n")
            continue
            
        # Evaluate using LLM-as-a-judge
        eval_result = eval_chain.invoke({
            "question": q,
            "expected": ", ".join(item["expected"]),
            "response": sys_resp
        })
        
        # Parse JSON from eval_result
        try:
            content = eval_result.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
                
            scores = json.loads(content)
            print(f"Scores: {scores}\n")
            results.append(scores)
        except Exception as e:
            print(f"Failed to parse eval response: {eval_result.content}\n")
            
        # Sleep slightly to respect rate limits
        time.sleep(2)
        
    # Aggregate scores
    if results:
        avg_relevance = sum(r.get("relevance_score", 0) for r in results) / len(results)
        avg_groundedness = sum(r.get("groundedness_score", 0) for r in results) / len(results)
        print("\n--- Evaluation Summary ---")
        print(f"Average Answer Relevance: {avg_relevance:.2f}")
        print(f"Average Answer Groundedness: {avg_groundedness:.2f}")

if __name__ == "__main__":
    evaluate_responses()
