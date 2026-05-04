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

        # Create Constraints for indexes and uniqueness
        labels = ["Service", "Database", "MessageBroker", "Team"]
        for label in labels:
            driver.execute_query(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE", database_="neo4j")

        # 1. Create Nodes
        print("Creating nodes...")
        
        # Services
        driver.execute_query(
            """
            UNWIND $batch AS row
            CREATE (s:Service {
                id: row.id, 
                name: row.name, 
                language: row.language, 
                memory_limit: row.memory_limit, 
                is_idempotent: row.is_idempotent
            })
            """,
            batch=data["nodes"]["Service"], database_="neo4j"
        )
            
        # Databases
        driver.execute_query(
            """
            UNWIND $batch AS row
            CREATE (d:Database {
                id: row.id, 
                name: row.name, 
                type: row.type, 
                sharding_enabled: row.sharding_enabled
            })
            """,
            batch=data["nodes"]["Database"], database_="neo4j"
        )
            
        # MessageBrokers
        driver.execute_query(
            """
            UNWIND $batch AS row
            CREATE (m:MessageBroker {
                id: row.id, 
                name: row.name, 
                type: row.type
            })
            """,
            batch=data["nodes"]["MessageBroker"], database_="neo4j"
        )
            
        # Teams
        driver.execute_query(
            """
            UNWIND $batch AS row
            CREATE (t:Team {
                id: row.id, 
                name: row.name, 
                on_call_phone: row.on_call_phone
            })
            """,
            batch=data["nodes"]["Team"], database_="neo4j"
        )

        print("Creating relationships...")
        # 2. Create Relationships
        
        # CALLS
        driver.execute_query(
            """
            UNWIND $batch AS row
            MATCH (source:Service {id: row.source})
            MATCH (target:Service {id: row.target})
            CREATE (source)-[:CALLS {protocol: row.protocol}]->(target)
            """,
            batch=data["edges"]["CALLS"], database_="neo4j"
        )
            
        # READS_FROM
        driver.execute_query(
            """
            UNWIND $batch AS row
            MATCH (source:Service {id: row.source})
            MATCH (target:Database {id: row.target})
            CREATE (source)-[:READS_FROM]->(target)
            """,
            batch=data["edges"]["READS_FROM"], database_="neo4j"
        )
            
        # WRITES_TO
        driver.execute_query(
            """
            UNWIND $batch AS row
            MATCH (source:Service {id: row.source})
            MATCH (target:Database {id: row.target})
            CREATE (source)-[:WRITES_TO {delivery_semantics: row.delivery_semantics}]->(target)
            """,
            batch=data["edges"]["WRITES_TO"], database_="neo4j"
        )
            
        # PUBLISHES_TO
        driver.execute_query(
            """
            UNWIND $batch AS row
            MATCH (source:Service {id: row.source})
            MATCH (target:MessageBroker {id: row.target})
            CREATE (source)-[:PUBLISHES_TO]->(target)
            """,
            batch=data["edges"]["PUBLISHES_TO"], database_="neo4j"
        )
            
        # MAINTAINS
        driver.execute_query(
            """
            UNWIND $batch AS row
            MATCH (source:Team {id: row.source})
            MATCH (target:Service {id: row.target})
            CREATE (source)-[:MAINTAINS]->(target)
            """,
            batch=data["edges"]["MAINTAINS"], database_="neo4j"
        )

        print("Ingestion complete.")

if __name__ == "__main__":
    ingest_data()
