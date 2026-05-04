import json
import os
import random
import uuid

def generate_synthetic_data():
    # Entities
    services = [
        {"id": str(uuid.uuid4()), "name": "api-gateway", "language": "Go", "memory_limit": "512MB", "is_idempotent": True},
        {"id": str(uuid.uuid4()), "name": "user-service", "language": "Java", "memory_limit": "1GB", "is_idempotent": False},
        {"id": str(uuid.uuid4()), "name": "billing-service", "language": "Python", "memory_limit": "2GB", "is_idempotent": True},
        {"id": str(uuid.uuid4()), "name": "inventory-service", "language": "Node.js", "memory_limit": "1GB", "is_idempotent": False},
        {"id": str(uuid.uuid4()), "name": "recommendation-service", "language": "Python", "memory_limit": "4GB", "is_idempotent": True},
        {"id": str(uuid.uuid4()), "name": "notification-service", "language": "Go", "memory_limit": "256MB", "is_idempotent": True},
    ]

    databases = [
        {"id": str(uuid.uuid4()), "name": "users-db", "type": "PostgreSQL", "sharding_enabled": False},
        {"id": str(uuid.uuid4()), "name": "billing-db", "type": "PostgreSQL", "sharding_enabled": True},
        {"id": str(uuid.uuid4()), "name": "inventory-db", "type": "MongoDB", "sharding_enabled": True},
        {"id": str(uuid.uuid4()), "name": "cache-redis", "type": "Redis", "sharding_enabled": False},
    ]

    message_brokers = [
        {"id": str(uuid.uuid4()), "name": "events-kafka", "type": "Kafka"},
        {"id": str(uuid.uuid4()), "name": "tasks-rabbitmq", "type": "RabbitMQ"},
    ]

    teams = [
        {"id": str(uuid.uuid4()), "name": "Platform Team", "on_call_phone": "+1-555-0100"},
        {"id": str(uuid.uuid4()), "name": "Core Services Team", "on_call_phone": "+1-555-0101"},
        {"id": str(uuid.uuid4()), "name": "Finance Team", "on_call_phone": "+1-555-0102"},
        {"id": str(uuid.uuid4()), "name": "Data Science Team", "on_call_phone": "+1-555-0103"},
    ]

    def get_id(entities, name):
        return next(e["id"] for e in entities if e["name"] == name)

    # Relationships
    calls = [
        {"source": get_id(services, "api-gateway"), "target": get_id(services, "user-service"), "protocol": "gRPC"},
        {"source": get_id(services, "api-gateway"), "target": get_id(services, "billing-service"), "protocol": "REST"},
        {"source": get_id(services, "api-gateway"), "target": get_id(services, "inventory-service"), "protocol": "REST"},
        {"source": get_id(services, "user-service"), "target": get_id(services, "recommendation-service"), "protocol": "gRPC"},
        {"source": get_id(services, "billing-service"), "target": get_id(services, "notification-service"), "protocol": "gRPC"},
    ]

    reads_from = [
        {"source": get_id(services, "user-service"), "target": get_id(databases, "users-db")},
        {"source": get_id(services, "user-service"), "target": get_id(databases, "cache-redis")},
        {"source": get_id(services, "billing-service"), "target": get_id(databases, "billing-db")},
        {"source": get_id(services, "inventory-service"), "target": get_id(databases, "inventory-db")},
        {"source": get_id(services, "inventory-service"), "target": get_id(databases, "cache-redis")},
    ]

    writes_to = [
        {"source": get_id(services, "user-service"), "target": get_id(databases, "users-db"), "delivery_semantics": "exactly-once"},
        {"source": get_id(services, "user-service"), "target": get_id(databases, "cache-redis"), "delivery_semantics": "at-least-once"},
        {"source": get_id(services, "billing-service"), "target": get_id(databases, "billing-db"), "delivery_semantics": "exactly-once"},
        {"source": get_id(services, "inventory-service"), "target": get_id(databases, "inventory-db"), "delivery_semantics": "exactly-once"},
        {"source": get_id(services, "inventory-service"), "target": get_id(databases, "cache-redis"), "delivery_semantics": "at-least-once"},
    ]

    publishes_to = [
        {"source": get_id(services, "user-service"), "target": get_id(message_brokers, "events-kafka")},
        {"source": get_id(services, "billing-service"), "target": get_id(message_brokers, "events-kafka")},
        {"source": get_id(services, "inventory-service"), "target": get_id(message_brokers, "events-kafka")},
        {"source": get_id(services, "notification-service"), "target": get_id(message_brokers, "tasks-rabbitmq")},
    ]

    maintains = [
        {"source": get_id(teams, "Platform Team"), "target": get_id(services, "api-gateway")},
        {"source": get_id(teams, "Core Services Team"), "target": get_id(services, "user-service")},
        {"source": get_id(teams, "Finance Team"), "target": get_id(services, "billing-service")},
        {"source": get_id(teams, "Core Services Team"), "target": get_id(services, "inventory-service")},
        {"source": get_id(teams, "Data Science Team"), "target": get_id(services, "recommendation-service")},
        {"source": get_id(teams, "Platform Team"), "target": get_id(services, "notification-service")},
    ]

    data = {
        "nodes": {
            "Service": services,
            "Database": databases,
            "MessageBroker": message_brokers,
            "Team": teams
        },
        "edges": {
            "CALLS": calls,
            "READS_FROM": reads_from,
            "WRITES_TO": writes_to,
            "PUBLISHES_TO": publishes_to,
            "MAINTAINS": maintains
        }
    }

    os.makedirs("data", exist_ok=True)
    with open("data/synthetic_architecture.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Successfully generated data/synthetic_architecture.json")

if __name__ == "__main__":
    generate_synthetic_data()
