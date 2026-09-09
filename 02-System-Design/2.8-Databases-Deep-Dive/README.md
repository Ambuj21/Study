# 🏗️ System Design — Topic 8: Databases Deep Dive — SQL & NoSQL

> **Why this matters**: Choosing the wrong database is the **most expensive mistake** in system design. It affects everything — performance, scalability, consistency, and developer productivity. Migrating databases after launch is like changing the engine of a plane mid-flight. Get it right from the start.

> **Prerequisite**: Topic 1.4 covered SQL basics (ACID, JOINs, indexing, normalization). This topic goes deeper from a **system design perspective**.

> **Code Implementation**: See [code.py](./code.py) for runnable Python simulations

---

## 🧠 SQL vs NoSQL — The Big Decision

### 🎯 Analogy
> - **SQL** is like a **library** — books are organized in strict categories with a card catalog. Finding anything is reliable and consistent, but reorganizing the shelves is painful.
> - **NoSQL** is like a **warehouse** — throw items in labeled bins. Super flexible and fast to store, but finding related items across bins requires more work.

```mermaid
graph TD
    DB["🗄️ Which Database?"] --> SQL["🔵 SQL (Relational)<br/>PostgreSQL, MySQL"]
    DB --> NOSQL["🟢 NoSQL (Non-Relational)"]

    NOSQL --> KV["🔑 Key-Value<br/>Redis, DynamoDB"]
    NOSQL --> DOC["📄 Document<br/>MongoDB, CouchDB"]
    NOSQL --> COL["📊 Column-Family<br/>Cassandra, HBase"]
    NOSQL --> GRAPH["🕸️ Graph<br/>Neo4j, Neptune"]

    style SQL fill:#3498db,stroke:#333,color:#fff,stroke-width:3px
    style KV fill:#2ecc71,stroke:#333,color:#fff
    style DOC fill:#27ae60,stroke:#333,color:#fff
    style COL fill:#1abc9c,stroke:#333,color:#fff
    style GRAPH fill:#16a085,stroke:#333,color:#fff
```

---

## 1️⃣ SQL (Relational) Databases — Deep Dive

### When SQL Shines

```
USE SQL WHEN:
  ✅ Data has clear RELATIONSHIPS (users → orders → products)
  ✅ You need ACID transactions (banking, e-commerce checkout)
  ✅ You need complex JOINs and aggregations
  ✅ Schema is well-defined and stable
  ✅ Data integrity is critical (no orphan records)
  ✅ You need strong consistency

REAL EXAMPLES:
  - Banking systems (transactions MUST be ACID)
  - E-commerce (orders + inventory + payments)
  - User management (roles, permissions, relationships)
  - ERP / CRM systems
```

### ACID — The SQL Guarantee

```mermaid
graph LR
    ACID["🛡️ ACID"] --> A["Atomicity<br/>All or nothing"]
    ACID --> C["Consistency<br/>Rules always enforced"]
    ACID --> I["Isolation<br/>Transactions don't interfere"]
    ACID --> D["Durability<br/>Committed = permanent"]

    style ACID fill:#3498db,stroke:#333,color:#fff,stroke-width:3px
```

### Pseudo Code — SQL Schema for E-commerce

```
// Relational schema — data is NORMALIZED (no duplication)

TABLE users:
    id          INTEGER PRIMARY KEY
    name        VARCHAR(100) NOT NULL
    email       VARCHAR(255) UNIQUE NOT NULL
    created_at  TIMESTAMP DEFAULT NOW()

TABLE products:
    id          INTEGER PRIMARY KEY
    name        VARCHAR(200)
    price       DECIMAL(10, 2)
    stock       INTEGER DEFAULT 0

TABLE orders:
    id          INTEGER PRIMARY KEY
    user_id     INTEGER REFERENCES users(id)    // Foreign key!
    total       DECIMAL(10, 2)
    status      ENUM('pending', 'paid', 'shipped')
    created_at  TIMESTAMP DEFAULT NOW()

TABLE order_items:
    id          INTEGER PRIMARY KEY
    order_id    INTEGER REFERENCES orders(id)
    product_id  INTEGER REFERENCES products(id)
    quantity    INTEGER
    price       DECIMAL(10, 2)

// POWER OF SQL: Complex queries across related data
QUERY "Revenue by product last 30 days":
    SELECT p.name, SUM(oi.quantity * oi.price) AS revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.id
    JOIN orders o ON oi.order_id = o.id
    WHERE o.created_at > NOW() - 30 DAYS
    AND o.status = 'paid'
    GROUP BY p.name
    ORDER BY revenue DESC
    LIMIT 10
```

---

## 2️⃣ NoSQL — The Four Types

### Type 1: Key-Value Store

```mermaid
graph LR
    subgraph "🔑 Key-Value (Redis, DynamoDB)"
        K1["session:abc123"] --> V1["{ user: Alice, cart: [Laptop] }"]
        K2["user:42:profile"] --> V2["{ name: Bob, age: 28 }"]
        K3["rate_limit:ip:1.2.3.4"] --> V3["{ count: 47, window: 60s }"]
    end

    style K1 fill:#e74c3c,stroke:#333,color:#fff
    style K2 fill:#e74c3c,stroke:#333,color:#fff
    style K3 fill:#e74c3c,stroke:#333,color:#fff
```

```
KEY-VALUE STORES:
  Data model:  Simple key → value pairs
  Speed:       Fastest (O(1) lookups)
  Scale:       Excellent horizontal scaling
  Use cases:   Caching, sessions, rate limiting, leaderboards
  Cannot do:   Complex queries, JOINs, aggregations
  Examples:    Redis, Memcached, DynamoDB, Riak

  Think of it as: A giant hash map / dictionary
```

### Type 2: Document Store

```mermaid
graph TD
    subgraph "📄 Document Store (MongoDB)"
        DOC1["Order Document"]
        DOC1 --> D1["{<br/>  _id: 'ord_123',<br/>  user: { name: 'Alice', email: '...' },<br/>  items: [<br/>    { product: 'Laptop', price: 999 },<br/>    { product: 'Mouse', price: 29 }<br/>  ],<br/>  total: 1028,<br/>  status: 'paid'<br/>}"]
    end

    style DOC1 fill:#27ae60,stroke:#333,color:#fff
```

```
DOCUMENT STORES:
  Data model:  JSON/BSON documents (nested, flexible schema)
  Speed:       Fast reads (all data in one document)
  Scale:       Good horizontal scaling
  Use cases:   Product catalogs, CMS, user profiles, events
  Cannot do:   Complex JOINs across collections
  Examples:    MongoDB, CouchDB, Firebase Firestore

  KEY DIFFERENCE FROM SQL:
    SQL:    User data in 'users' table, address in 'addresses' table → JOIN
    NoSQL:  User + address + preferences ALL in one document → no JOIN needed

  DENORMALIZED = Faster reads, harder updates
```

### Type 3: Column-Family Store

```
COLUMN-FAMILY STORES:
  Data model:  Rows with dynamic columns, grouped into column families
  Speed:       Extremely fast writes (append-only)
  Scale:       Best horizontal scaling (linear with nodes)
  Use cases:   Time-series, IoT, logs, analytics, event tracking
  Cannot do:   Ad-hoc queries, JOINs
  Examples:    Cassandra, HBase, ScyllaDB

  HOW IT'S DIFFERENT:
    SQL row:     [id, name, email, age, city, ...]  ← ALL columns stored together
    Column-family: Columns stored SEPARATELY on disk
                   Reading just 'name' doesn't load 'email', 'age', etc.
                   MUCH faster for analytical queries on specific columns
```

### Type 4: Graph Database

```mermaid
graph LR
    A["👤 Alice"] -->|"FOLLOWS"| B["👤 Bob"]
    B -->|"FOLLOWS"| C["👤 Charlie"]
    A -->|"LIKES"| P1["📝 Post 1"]
    B -->|"LIKES"| P1
    C -->|"WROTE"| P1
    A -->|"FRIENDS"| B

    style A fill:#3498db,stroke:#333,color:#fff
    style B fill:#2ecc71,stroke:#333,color:#fff
    style C fill:#f39c12,stroke:#333,color:#fff
    style P1 fill:#9b59b6,stroke:#333,color:#fff
```

```
GRAPH DATABASES:
  Data model:  Nodes + Edges (relationships are first-class)
  Speed:       Fastest for relationship traversal
  Scale:       Moderate (hard to partition graphs)
  Use cases:   Social networks, recommendations, fraud detection, knowledge graphs
  Cannot do:   Aggregate queries, heavy writes
  Examples:    Neo4j, Amazon Neptune, ArangoDB

  WHY NOT SQL FOR GRAPHS?
    SQL: "Find friends of friends of friends" = 3 nested JOINs = SLOW
    Graph: Traverse 3 edges = FAST (regardless of data size)
```

---

## 3️⃣ ACID vs BASE

```mermaid
graph LR
    subgraph "🔵 ACID (SQL)"
        A1["Atomic"]
        A2["Consistent"]
        A3["Isolated"]
        A4["Durable"]
    end

    subgraph "🟢 BASE (NoSQL)"
        B1["Basically Available"]
        B2["Soft state"]
        B3["Eventually consistent"]
    end

    style A1 fill:#3498db,stroke:#333,color:#fff
    style B1 fill:#2ecc71,stroke:#333,color:#fff
```

| Property | ACID (SQL) | BASE (NoSQL) |
|----------|-----------|-------------|
| **Consistency** | Strong — always correct | Eventual — correct *soon* |
| **Availability** | May block during contention | Always responds |
| **Speed** | Slower (locking, coordination) | Faster (no coordination) |
| **Scale** | Vertical (mostly) | Horizontal (designed for it) |
| **Use case** | Banking, orders | Social media, analytics |

---

## 4️⃣ Indexing Deep Dive — How Databases Find Data Fast

### 📊 Without Index vs With Index

```mermaid
graph LR
    subgraph "❌ No Index — Full Table Scan"
        SCAN["Check EVERY row<br/>1 million rows = 1M checks<br/>O(n) = SLOW"]
    end

    subgraph "✅ B-Tree Index"
        TREE["Binary search through tree<br/>1 million rows = ~20 checks<br/>O(log n) = FAST"]
    end

    style SCAN fill:#e74c3c,stroke:#333,color:#fff
    style TREE fill:#2ecc71,stroke:#333,color:#fff
```

### Index Types

```
B-TREE INDEX (default in PostgreSQL, MySQL):
  Structure:   Balanced tree, sorted
  Best for:    Range queries (WHERE age > 25 AND age < 35)
               Equality (WHERE id = 42)
               Sorting (ORDER BY created_at)
  Time:        O(log n) for all operations
  Used by:     PostgreSQL, MySQL, SQLite

HASH INDEX:
  Structure:   Hash table
  Best for:    Exact equality ONLY (WHERE id = 42)
  Cannot do:   Range queries, sorting
  Time:        O(1) average
  Used by:     Redis, Memcached, DynamoDB

LSM TREE (Log-Structured Merge Tree):
  Structure:   In-memory buffer + sorted disk files
  Best for:    WRITE-HEAVY workloads
  Trade-off:   Faster writes, slightly slower reads
  Used by:     Cassandra, RocksDB, LevelDB, ClickHouse

COMPOSITE INDEX:
  CREATE INDEX idx ON users(country, city, age)
  Speeds up:  WHERE country = 'US'
              WHERE country = 'US' AND city = 'NYC'
              WHERE country = 'US' AND city = 'NYC' AND age > 25
  Doesn't help: WHERE city = 'NYC'  (must use leftmost columns!)
```

### Pseudo Code — Index Trade-offs

```
// INDEX TRADE-OFFS — Indexes aren't free!

// BENEFIT: Faster reads
// Without index: SELECT * FROM users WHERE email = ?  → Scan 10M rows (~500ms)
// With index:    SELECT * FROM users WHERE email = ?  → B-tree lookup (~1ms)
// Speedup: 500x!

// COST: Slower writes
// Without index: INSERT INTO users → Just append (~1ms)
// With index:    INSERT INTO users → Append + update B-tree (~5ms)
// Every index adds ~2-5ms to each write

// COST: Storage
// Each index uses ~10-30% of table size
// 5 indexes on a 10GB table = 5-15 GB extra storage

// RULE OF THUMB:
// Read-heavy tables (95% reads): Add many indexes
// Write-heavy tables (logs, events): Minimize indexes
// Max recommended: 5-7 indexes per table
```

---

## 5️⃣ Connection Pooling — Don't Open 10,000 Connections

### The Problem

```
WITHOUT CONNECTION POOL:
  Each request opens a new DB connection (~50ms)
  Each connection uses ~10MB of RAM
  1,000 concurrent users = 1,000 connections = 10 GB RAM!
  PostgreSQL default max: 100 connections → CRASH at 101!

WITH CONNECTION POOL (PgBouncer):
  Pool of 50 reusable connections
  1,000 concurrent requests share 50 connections
  Connection reuse: ~0.1ms (vs 50ms to create new)
  RAM: 500 MB instead of 10 GB
```

```mermaid
graph TD
    subgraph "App Servers (1000 threads)"
        T1["Thread 1"]
        T2["Thread 2"]
        T3["..."]
        T4["Thread 1000"]
    end

    subgraph "Connection Pool (50 connections)"
        C1["Conn 1"]
        C2["Conn 2"]
        C3["..."]
        C4["Conn 50"]
    end

    T1 & T2 & T3 & T4 --> POOL["🔄 Pool Manager<br/>Reuses connections"]
    POOL --> C1 & C2 & C3 & C4

    C1 & C2 & C3 & C4 --> DB["🗄️ PostgreSQL"]

    style POOL fill:#f39c12,stroke:#333,color:#fff,stroke-width:3px
```

---

## 6️⃣ The Database Selection Framework

```mermaid
graph TD
    START["🤔 Which database?"] --> Q1{"Need ACID<br/>transactions?"}

    Q1 -->|"Yes"| Q2{"Scale beyond<br/>1 server?"}
    Q1 -->|"No"| Q3{"Data structure?"}

    Q2 -->|"No"| PG["🐘 PostgreSQL<br/>(best general purpose)"]
    Q2 -->|"Yes"| Q4{"Write-heavy?"}

    Q4 -->|"No"| PGREAD["🐘 PostgreSQL<br/>+ Read Replicas"]
    Q4 -->|"Yes"| SHARD["🐘 PostgreSQL sharded<br/>or CockroachDB"]

    Q3 -->|"Key-Value"| REDIS["⚡ Redis"]
    Q3 -->|"Documents (JSON)"| MONGO["🍃 MongoDB"]
    Q3 -->|"Time series / Logs"| CASS["📊 Cassandra"]
    Q3 -->|"Relationships / Graph"| NEO["🕸️ Neo4j"]

    style PG fill:#3498db,stroke:#333,color:#fff,stroke-width:3px
    style REDIS fill:#e74c3c,stroke:#333,color:#fff
    style MONGO fill:#2ecc71,stroke:#333,color:#fff
    style CASS fill:#f39c12,stroke:#333,color:#fff
```

### The Decision Table

| Requirement | Best Choice | Why |
|------------|-------------|-----|
| General purpose, unsure | **PostgreSQL** | Does everything well, huge ecosystem |
| Caching, sessions, queues | **Redis** | Fastest, rich data structures |
| Flexible schema, rapid iteration | **MongoDB** | Schema-less, easy for prototyping |
| Write-heavy time-series/logs | **Cassandra** | Linear write scaling, append-only |
| Social graph, recommendations | **Neo4j** | O(1) relationship traversal |
| Full-text search | **Elasticsearch** | Inverted index, scoring |
| Analytics, OLAP | **ClickHouse** | Columnar, 100x faster than SQL for analytics |
| Global ACID + horizontal scale | **CockroachDB / Spanner** | Distributed SQL |

---

## 7️⃣ How Real Companies Choose

```
NETFLIX:
  ├── Cassandra    → Viewing history, user activity (write-heavy, AP)
  ├── MySQL        → Billing, accounts (ACID required)
  ├── Elasticsearch → Search catalog
  └── Redis        → Session cache, recommendations cache

UBER:
  ├── MySQL (Schemaless) → Trip data, user data (custom sharding)
  ├── PostgreSQL   → Geospatial queries (PostGIS)
  ├── Redis        → Real-time supply/demand pricing
  └── Cassandra    → Logging, analytics

INSTAGRAM:
  ├── PostgreSQL   → User data, photos metadata (sharded)
  ├── Cassandra    → Feed storage, direct messages
  ├── Redis        → Caching, rate limiting
  └── Elasticsearch → Search (users, hashtags)

LESSON: Big companies use MULTIPLE databases!
  Each database is chosen for what it does BEST.
  This is called "polyglot persistence".
```

---

## 8️⃣ SQL vs NoSQL — The Final Comparison

| Factor | SQL | NoSQL |
|--------|-----|-------|
| **Schema** | Fixed, strict | Flexible, dynamic |
| **Relationships** | ⭐ Excellent (JOINs) | Poor (denormalized) |
| **Transactions** | ⭐ ACID guaranteed | Limited or eventual |
| **Scaling** | Vertical (mostly) | ⭐ Horizontal (native) |
| **Write speed** | Good | ⭐ Excellent (esp. Cassandra) |
| **Query flexibility** | ⭐ SQL is powerful | Limited query language |
| **Schema changes** | Painful (migrations) | ⭐ Easy (just add fields) |
| **Learning curve** | Medium | Low (for basic use) |
| **Maturity** | 40+ years | 10-20 years |
| **Default choice** | ⭐ Start here | When SQL doesn't fit |

---

## 🏋️ Practice Exercises

### Exercise 1: Choose the Database
> For each system, pick the best database(s) and justify:
> - a) Banking system with transfers between accounts
> - b) Real-time chat application (WhatsApp-like)
> - c) IoT platform receiving 100,000 sensor readings/second
> - d) Social network with friend recommendations
> - e) Content management system for a news website

### Exercise 2: Design the Schema
> Design both SQL and NoSQL schemas for a food delivery app (users, restaurants, menus, orders, reviews). Which would you choose for production and why?

### Exercise 3: Index Strategy
> Your `orders` table has 50 million rows. Common queries:
> - Find orders by user_id (90% of queries)
> - Find orders by date range (5%)
> - Find orders by status (3%)
> - Find orders by user_id + status (2%)
> Design the optimal index strategy. How much extra storage?

---

## 🎤 Interview Corner

> **Q: "SQL or NoSQL — how do you decide?"**
>
> **Great answer**: "I start with PostgreSQL as the default — it handles 90% of use cases with ACID transactions, JOINs, and even JSON support. I'd switch to NoSQL only when there's a specific need: Redis for caching and real-time data, Cassandra for write-heavy time-series data, MongoDB when schema flexibility is critical and relationships are minimal, or Neo4j for graph traversal problems. Most production systems are polyglot — using multiple databases for different workloads."

> **Q: "How do you scale a relational database?"**
>
> **Great answer**: "I'd scale in this order: First, add caching with Redis to reduce read load by 80%. Second, add read replicas to spread reads across multiple servers. Third, optimize queries and indexes using EXPLAIN. Fourth, vertical scaling — bigger machine. Only as a last resort would I shard the database, because sharding adds enormous complexity — cross-shard JOINs, distributed transactions, rebalancing. Most companies never need sharding — Netflix, GitHub, and Stack Overflow all run on replicated PostgreSQL."

---

## ✅ Key Takeaways

| Concept | Remember |
|---------|----------|
| **Default choice** | PostgreSQL — does everything well, start here |
| **Key-Value (Redis)** | O(1) lookups, caching, sessions, rate limiting |
| **Document (MongoDB)** | Flexible schema, nested JSON, rapid prototyping |
| **Column-Family (Cassandra)** | Write-heavy, time-series, linear horizontal scale |
| **Graph (Neo4j)** | Relationships are first-class, social networks |
| **ACID vs BASE** | ACID = strong consistency (SQL). BASE = eventual consistency (NoSQL) |
| **B-tree index** | Default, O(log n), good for ranges and equality |
| **Connection pooling** | 50 pooled connections > 1,000 individual connections |
| **Polyglot persistence** | Use multiple databases — each for what it does best |

---

**Next up → [Topic 9: Database Replication](../2.9-Database-Replication/)**
