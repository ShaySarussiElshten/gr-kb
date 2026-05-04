import requests
import json
import time

QUESTIONS = [
    "Which service does the API Gateway call?",
    "List all databases in the architecture.",
    "Which team maintains the recommendation service?",
    "Are there any databases that have sharding enabled?",
    "Which language is the inventory-service written in?",
    "What message brokers are being used?",
    "Which services publish to Kafka?",
    "Does the notification-service publish to any message broker?",
    "What is the memory limit of the user-service?",
    "Which services are idempotent?",
    "List all services maintained by the Core Services Team.",
    "What is the on-call phone number for the team maintaining the billing-service?",
    "Which services read from PostgreSQL databases?",
    "Are there any services written in Go?",
    "Which databases have exactly-once delivery semantics for writes?",
    "List all services that communicate via gRPC.",
    "Which services write to the cache-redis database?",
    "Which team maintains the API Gateway?",
    "How many microservices are there in total?",
    "Show me the path of a request from the API Gateway to the billing database."
]

def run_tests():
    url = "http://localhost:8005/chat"
    
    with open("test_results.md", "w", encoding="utf-8") as f:
        f.write("# 20 Questions Graph RAG Test Results\n\n")
        
        for i, q in enumerate(QUESTIONS, 1):
            print(f"Asking question {i}/20: {q}")
            f.write(f"### Q{i}: {q}\n")
            
            try:
                response = requests.post(url, json={"message": q}, timeout=60)
                if response.status_code == 200:
                    answer = response.json().get("response", "No response")
                    f.write(f"**Answer:** {answer}\n\n")
                else:
                    f.write(f"**Error:** Backend returned status {response.status_code}\n\n")
            except Exception as e:
                f.write(f"**Exception:** {str(e)}\n\n")

if __name__ == "__main__":
    run_tests()
    print("Done! Results saved to test_results.md")
