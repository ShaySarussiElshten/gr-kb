import json
import os
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")

def ingest_data():
    with open("data/synthetic_architecture.json", "r") as f:
        data = json.load(f)

    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # Clear existing data
        driver.execute_query("MATCH (n) DETACH DELETE n", database_="neo4j")

        # 1. Create Nodes
        print("Creating nodes...")
        
        # Services
        for node in data["nodes"]["Service"]:
            driver.execute_query(
                """
                CREATE (s:Service {
                    id: $id, 
                    name: $name, 
                    language: $language, 
                    memory_limit: $memory_limit, 
                    is_idempotent: $is_idempotent
                })
                """,
                id=node["id"], name=node["name"], language=node["language"],
                memory_limit=node["memory_limit"], is_idempotent=node["is_idempotent"],
                database_="neo4j",
            )
            
        # Databases
        for node in data["nodes"]["Database"]:
            driver.execute_query(
                """
                CREATE (d:Database {
                    id: $id, 
                    name: $name, 
                    type: $type, 
                    sharding_enabled: $sharding_enabled
                })
                """,
                id=node["id"], name=node["name"], type=node["type"],
                sharding_enabled=node["sharding_enabled"],
                database_="neo4j",
            )
            
        # MessageBrokers
        for node in data["nodes"]["MessageBroker"]:
            driver.execute_query(
                """
                CREATE (m:MessageBroker {
                    id: $id, 
                    name: $name, 
                    type: $type
                })
                """,
                id=node["id"], name=node["name"], type=node["type"],
                database_="neo4j",
            )
            
        # Teams
        for node in data["nodes"]["Team"]:
            driver.execute_query(
                """
                CREATE (t:Team {
                    id: $id, 
                    name: $name, 
                    on_call_phone: $on_call_phone
                })
                """,
                id=node["id"], name=node["name"], on_call_phone=node["on_call_phone"],
                database_="neo4j",
            )

        print("Creating relationships...")
        # 2. Create Relationships
        
        # CALLS
        for edge in data["edges"]["CALLS"]:
            driver.execute_query(
                """
                MATCH (source:Service {id: $source_id})
                MATCH (target:Service {id: $target_id})
                CREATE (source)-[:CALLS {protocol: $protocol}]->(target)
                """,
                source_id=edge["source"], target_id=edge["target"], protocol=edge["protocol"],
                database_="neo4j",
            )
            
        # READS_FROM
        for edge in data["edges"]["READS_FROM"]:
            driver.execute_query(
                """
                MATCH (source:Service {id: $source_id})
                MATCH (target:Database {id: $target_id})
                CREATE (source)-[:READS_FROM]->(target)
                """,
                source_id=edge["source"], target_id=edge["target"],
                database_="neo4j",
            )
            
        # WRITES_TO
        for edge in data["edges"]["WRITES_TO"]:
            driver.execute_query(
                """
                MATCH (source:Service {id: $source_id})
                MATCH (target:Database {id: $target_id})
                CREATE (source)-[:WRITES_TO {delivery_semantics: $delivery_semantics}]->(target)
                """,
                source_id=edge["source"], target_id=edge["target"], delivery_semantics=edge["delivery_semantics"],
                database_="neo4j",
            )
            
        # PUBLISHES_TO
        for edge in data["edges"]["PUBLISHES_TO"]:
            driver.execute_query(
                """
                MATCH (source:Service {id: $source_id})
                MATCH (target:MessageBroker {id: $target_id})
                CREATE (source)-[:PUBLISHES_TO]->(target)
                """,
                source_id=edge["source"], target_id=edge["target"],
                database_="neo4j",
            )
            
        # MAINTAINS
        for edge in data["edges"]["MAINTAINS"]:
            driver.execute_query(
                """
                MATCH (source:Team {id: $source_id})
                MATCH (target:Service {id: $target_id})
                CREATE (source)-[:MAINTAINS]->(target)
                """,
                source_id=edge["source"], target_id=edge["target"],
                database_="neo4j",
            )

        print("Ingestion complete.")

if __name__ == "__main__":
    ingest_data()
