# 20 Questions Graph RAG Test Results

### Q1: Which service does the API Gateway call?
**Answer:** I couldn't find any information about which service the API Gateway calls. The query was successful but returned no results.

### Q2: List all databases in the architecture.
**Answer:** The databases in the architecture are:

*   **users-db**: PostgreSQL, sharding disabled.
*   **billing-db**: PostgreSQL, sharding enabled.
*   **inventory-db**: MongoDB, sharding enabled.
*   **cache-redis**: Redis, sharding disabled.

### Q3: Which team maintains the recommendation service?
**Answer:** The Data Science Team maintains the recommendation service.

### Q4: Are there any databases that have sharding enabled?
**Answer:** Yes, there are two databases with sharding enabled:

*   **billing-db**: A PostgreSQL database.
*   **inventory-db**: A MongoDB database.

### Q5: Which language is the inventory-service written in?
**Answer:** The inventory-service is written in Node.js.

### Q6: What message brokers are being used?
**Answer:** The company is using two message brokers: `events-kafka` (Kafka) and `tasks-rabbitmq` (RabbitMQ).

### Q7: Which services publish to Kafka?
**Answer:** The following services publish to Kafka: user-service, billing-service, and inventory-service.

### Q8: Does the notification-service publish to any message broker?
**Answer:** Yes, the notification-service does publish to a message broker.

### Q9: What is the memory limit of the user-service?
**Answer:** The memory limit of the user-service is 1GB.

### Q10: Which services are idempotent?
**Answer:** The following services are idempotent: api-gateway, billing-service, recommendation-service, and notification-service.

### Q11: List all services maintained by the Core Services Team.
**Answer:** The Core Services Team maintains the following services: user-service and inventory-service.

### Q12: What is the on-call phone number for the team maintaining the billing-service?
**Answer:** The on-call phone number for the team maintaining the billing-service is +1-555-0102.

### Q13: Which services read from PostgreSQL databases?
**Answer:** The user-service and billing-service read from PostgreSQL databases.

### Q14: Are there any services written in Go?
**Answer:** Yes, there are two services written in Go: "api-gateway" and "notification-service".

### Q15: Which databases have exactly-once delivery semantics for writes?
**Answer:** The `users-db` (PostgreSQL), `billing-db` (PostgreSQL), and `inventory-db` (MongoDB) databases have exactly-once delivery semantics for writes.

### Q16: List all services that communicate via gRPC.
**Answer:** The following services communicate via gRPC:

*   **api-gateway** (Go) communicates with **user-service** (Java).
*   **user-service** (Java) communicates with **recommendation-service** (Python).
*   **billing-service** (Python) communicates with **notification-service** (Go).

### Q17: Which services write to the cache-redis database?
**Answer:** The user-service and inventory-service write to the cache-redis database.

### Q18: Which team maintains the API Gateway?
**Answer:** I couldn't find information about which team maintains the API Gateway. Is there anything else I can help with?

### Q19: How many microservices are there in total?
**Answer:** There are 6 microservices in total.

### Q20: Show me the path of a request from the API Gateway to the billing database.
**Answer:** I couldn't find a path from the API Gateway to the billing database in the architecture. It's possible that such a direct path doesn't exist or the information is not available in the graph database.

