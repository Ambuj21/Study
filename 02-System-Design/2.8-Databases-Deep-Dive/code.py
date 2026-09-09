"""
System Design Topic 8 - Databases Deep Dive: Python Simulations

Demonstrates:
- SQL vs NoSQL data modeling comparison
- B-Tree index simulation with performance measurement
- Document store vs relational query patterns
- Connection pooling impact
- Database selection quiz

Usage:
    python code.py
"""
import time
import random
import sqlite3
import json
import threading
from dataclasses import dataclass, field
from collections import defaultdict, OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed


# ================================================================
# 1. SQL vs DOCUMENT STORE — Same Data, Different Models
# ================================================================

print("=" * 60)
print("  1. SQL vs DOCUMENT — Same Data, Different Models")
print("=" * 60)

# --- SQL Model (Normalized) ---
sql_db = sqlite3.connect(":memory:")
cursor = sql_db.cursor()

cursor.executescript("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE
    );
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        total REAL,
        status TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER REFERENCES orders(id),
        product_name TEXT,
        quantity INTEGER,
        price REAL
    );
""")

# Insert sample data
cursor.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@mail.com')")
cursor.execute("INSERT INTO orders VALUES (1, 1, 1028.99, 'paid', '2024-01-15')")
cursor.execute("INSERT INTO order_items VALUES (1, 1, 'Laptop', 1, 999.99)")
cursor.execute("INSERT INTO order_items VALUES (2, 1, 'Mouse', 1, 29.00)")
sql_db.commit()

# SQL query — JOIN across 3 tables
print(f"\n  --- SQL (Normalized — 3 tables with JOINs) ---")
result = cursor.execute("""
    SELECT u.name, o.total, o.status,
           GROUP_CONCAT(oi.product_name || ' x' || oi.quantity)
    FROM users u
    JOIN orders o ON u.id = o.user_id
    JOIN order_items oi ON o.id = oi.order_id
    WHERE u.id = 1
    GROUP BY o.id
""").fetchone()
print(f"    Query: JOIN users + orders + order_items")
print(f"    Result: {result[0]} | ${result[1]} | {result[2]} | Items: {result[3]}")
print(f"    Tables touched: 3 (users, orders, order_items)")

# --- Document Model (Denormalized) ---
print(f"\n  --- DOCUMENT (Denormalized — 1 document) ---")
order_document = {
    "_id": "ord_001",
    "user": {"name": "Alice", "email": "alice@mail.com"},
    "items": [
        {"product": "Laptop", "quantity": 1, "price": 999.99},
        {"product": "Mouse", "quantity": 1, "price": 29.00},
    ],
    "total": 1028.99,
    "status": "paid",
    "created_at": "2024-01-15",
}
print(f"    Query: Get document by _id")
print(f"    Result: {order_document['user']['name']} | ${order_document['total']} | {order_document['status']}")
items_str = ", ".join(f"{i['product']} x{i['quantity']}" for i in order_document["items"])
print(f"    Items: {items_str}")
print(f"    Tables touched: 1 (single document, no JOINs!)")

print(f"\n  SQL: 3 tables + JOIN = More flexible queries, normalized data")
print(f"  Doc: 1 document     = Faster reads, but data duplication")

print()


# ================================================================
# 2. B-TREE INDEX SIMULATION
# ================================================================

print("=" * 60)
print("  2. B-TREE INDEX — Why Indexes Make Queries 1000x Faster")
print("=" * 60)

# Create a table with 100K rows
db = sqlite3.connect(":memory:")
cur = db.cursor()

cur.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price REAL,
        category TEXT
    )
""")

# Insert 100K products
categories = ["Electronics", "Books", "Clothing", "Food", "Sports"]
print(f"\n  Inserting 100,000 products...")
start = time.perf_counter()

cur.executemany(
    "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
    [(f"Product_{i}", round(random.uniform(1, 1000), 2), random.choice(categories))
     for i in range(100_000)]
)
db.commit()
insert_time = (time.perf_counter() - start) * 1000
print(f"  Insert time: {insert_time:.0f}ms")

# Query WITHOUT index
print(f"\n  --- Query WITHOUT index ---")
start = time.perf_counter()
for _ in range(100):
    cur.execute("SELECT * FROM products WHERE category = 'Electronics' AND price > 500")
    cur.fetchall()
no_index_time = (time.perf_counter() - start) * 1000
print(f"    100 queries: {no_index_time:.1f}ms ({no_index_time/100:.2f}ms per query)")

# EXPLAIN the query plan
plan = cur.execute("EXPLAIN QUERY PLAN SELECT * FROM products WHERE category = 'Electronics' AND price > 500").fetchone()
print(f"    Query plan: {plan[-1]}")

# Create index
print(f"\n  --- Creating index on (category, price) ---")
start = time.perf_counter()
cur.execute("CREATE INDEX idx_cat_price ON products(category, price)")
db.commit()
index_time = (time.perf_counter() - start) * 1000
print(f"    Index creation time: {index_time:.0f}ms")

# Query WITH index
print(f"\n  --- Query WITH index ---")
start = time.perf_counter()
for _ in range(100):
    cur.execute("SELECT * FROM products WHERE category = 'Electronics' AND price > 500")
    cur.fetchall()
with_index_time = (time.perf_counter() - start) * 1000
print(f"    100 queries: {with_index_time:.1f}ms ({with_index_time/100:.2f}ms per query)")

plan = cur.execute("EXPLAIN QUERY PLAN SELECT * FROM products WHERE category = 'Electronics' AND price > 500").fetchone()
print(f"    Query plan: {plan[-1]}")

speedup = no_index_time / with_index_time
print(f"\n  INDEX SPEEDUP: {speedup:.0f}x faster!")
print(f"  Without: Full table scan (checks all 100K rows)")
print(f"  With:    B-tree lookup (checks ~20 nodes)")

# Show index cost on writes
print(f"\n  --- Index cost on WRITES ---")
start = time.perf_counter()
for i in range(1000):
    cur.execute("INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
                (f"New_{i}", random.uniform(1, 100), random.choice(categories)))
db.commit()
write_with_index = (time.perf_counter() - start) * 1000

# Drop index and test writes
cur.execute("DROP INDEX idx_cat_price")
db.commit()
start = time.perf_counter()
for i in range(1000):
    cur.execute("INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
                (f"New2_{i}", random.uniform(1, 100), random.choice(categories)))
db.commit()
write_no_index = (time.perf_counter() - start) * 1000

print(f"    1,000 inserts WITHOUT index: {write_no_index:.1f}ms")
print(f"    1,000 inserts WITH index:    {write_with_index:.1f}ms")
print(f"    Index write overhead: {(write_with_index/write_no_index - 1)*100:.0f}% slower writes")
print(f"    Trade-off: Faster reads, slower writes. Worth it for read-heavy tables!")

print()


# ================================================================
# 3. KEY-VALUE STORE SIMULATION
# ================================================================

print("=" * 60)
print("  3. KEY-VALUE STORE — Redis-like Operations")
print("=" * 60)


class MiniRedis:
    """Simulates Redis data structures."""

    def __init__(self):
        self.data = {}
        self.expiry = {}
        self.ops = 0

    # String operations
    def set(self, key: str, value, ttl: float = None):
        self.data[key] = value
        if ttl:
            self.expiry[key] = time.time() + ttl
        self.ops += 1

    def get(self, key: str):
        if key in self.expiry and time.time() > self.expiry[key]:
            del self.data[key]
            del self.expiry[key]
            return None
        self.ops += 1
        return self.data.get(key)

    # Hash operations (like Redis HSET/HGET)
    def hset(self, key: str, field: str, value):
        if key not in self.data:
            self.data[key] = {}
        self.data[key][field] = value
        self.ops += 1

    def hget(self, key: str, field: str):
        self.ops += 1
        return self.data.get(key, {}).get(field)

    def hgetall(self, key: str):
        self.ops += 1
        return self.data.get(key, {})

    # Sorted set (like Redis ZADD/ZRANGE)
    def zadd(self, key: str, member: str, score: float):
        if key not in self.data:
            self.data[key] = []
        self.data[key].append((score, member))
        self.data[key].sort(key=lambda x: x[0], reverse=True)
        self.ops += 1

    def zrange(self, key: str, start: int, stop: int):
        self.ops += 1
        return self.data.get(key, [])[start:stop + 1]

    # Counter operations
    def incr(self, key: str, amount: int = 1) -> int:
        self.data[key] = self.data.get(key, 0) + amount
        self.ops += 1
        return self.data[key]


redis = MiniRedis()

# Demo: Session management
print(f"\n  --- Use Case 1: Session Management ---")
redis.hset("session:abc123", "user", "Alice")
redis.hset("session:abc123", "role", "admin")
redis.hset("session:abc123", "cart", json.dumps(["Laptop", "Mouse"]))
session = redis.hgetall("session:abc123")
print(f"    Session data: {session}")

# Demo: Rate limiting
print(f"\n  --- Use Case 2: Rate Limiting ---")
client_ip = "192.168.1.42"
for i in range(5):
    count = redis.incr(f"rate:{client_ip}")
    allowed = "ALLOWED" if count <= 3 else "BLOCKED"
    print(f"    Request {i+1} from {client_ip}: count={count} → {allowed}")

# Demo: Leaderboard
print(f"\n  --- Use Case 3: Leaderboard (Sorted Set) ---")
redis.zadd("leaderboard:game1", "Alice", 2500)
redis.zadd("leaderboard:game1", "Bob", 1800)
redis.zadd("leaderboard:game1", "Charlie", 3200)
redis.zadd("leaderboard:game1", "Diana", 2900)

top_3 = redis.zrange("leaderboard:game1", 0, 2)
for rank, (score, name) in enumerate(top_3, 1):
    print(f"    #{rank}: {name} — {score} points")

# Performance benchmark
print(f"\n  --- Performance: Key-Value vs SQL ---")
start = time.perf_counter()
for i in range(10_000):
    redis.set(f"key:{i}", f"value:{i}")
    redis.get(f"key:{i}")
kv_time = (time.perf_counter() - start) * 1000

start = time.perf_counter()
kv_db = sqlite3.connect(":memory:")
kv_cur = kv_db.cursor()
kv_cur.execute("CREATE TABLE kv (key TEXT PRIMARY KEY, value TEXT)")
for i in range(10_000):
    kv_cur.execute("INSERT OR REPLACE INTO kv VALUES (?, ?)", (f"key:{i}", f"value:{i}"))
    kv_cur.execute("SELECT value FROM kv WHERE key = ?", (f"key:{i}",))
kv_db.commit()
sql_time = (time.perf_counter() - start) * 1000

print(f"    10,000 SET+GET operations:")
print(f"    Key-Value (in-memory): {kv_time:.1f}ms")
print(f"    SQLite:                {sql_time:.1f}ms")
print(f"    Key-Value is {sql_time/kv_time:.1f}x faster for simple lookups!")

print()


# ================================================================
# 4. CONNECTION POOLING SIMULATION
# ================================================================

print("=" * 60)
print("  4. CONNECTION POOLING — Why 50 connections > 1,000")
print("=" * 60)


class ConnectionPool:
    """Simulates a database connection pool."""

    def __init__(self, max_connections: int = 10):
        self.max = max_connections
        self.available = max_connections
        self.lock = threading.Lock()
        self.total_served = 0
        self.total_waited = 0

    def acquire(self) -> float:
        """Get a connection. Returns wait time in ms."""
        wait_start = time.perf_counter()
        while True:
            with self.lock:
                if self.available > 0:
                    self.available -= 1
                    self.total_served += 1
                    return (time.perf_counter() - wait_start) * 1000
            self.total_waited += 1
            time.sleep(0.001)  # Wait and retry

    def release(self):
        with self.lock:
            self.available += 1


def simulate_pool(pool_size: int, num_requests: int, query_time_ms: float = 10):
    """Simulate concurrent DB access with a connection pool."""
    pool = ConnectionPool(pool_size)
    wait_times = []

    def worker():
        wait = pool.acquire()
        wait_times.append(wait)
        time.sleep(query_time_ms / 1000)  # Simulate query
        pool.release()

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(worker) for _ in range(num_requests)]
        for f in as_completed(futures):
            f.result()

    total_time = (time.perf_counter() - start) * 1000
    avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0
    max_wait = max(wait_times) if wait_times else 0

    return total_time, avg_wait, max_wait


NUM_REQUESTS = 200

print(f"\n  {NUM_REQUESTS} concurrent requests, 10ms query time each:")
print(f"\n  {'Pool Size':>10} {'Total Time':>12} {'Avg Wait':>12} {'Max Wait':>12}")
print(f"  {'─'*10} {'─'*12} {'─'*12} {'─'*12}")

for pool_size in [5, 10, 20, 50, 100, 200]:
    total, avg_w, max_w = simulate_pool(pool_size, NUM_REQUESTS)
    print(f"  {pool_size:>10} {total:>10.0f}ms {avg_w:>10.1f}ms {max_w:>10.1f}ms")

print(f"""
  INSIGHTS:
  ├── Too few connections (5): Requests queue up, high wait times
  ├── Sweet spot (20-50): Good throughput, reasonable waits
  ├── Too many (200): No benefit, wastes DB memory
  └── PostgreSQL default max: 100 connections
      Use PgBouncer to multiplex thousands of app connections
      into ~50 actual DB connections""")


print("\n" + "=" * 60)
print("  System Design Topic 8 Complete!")
print("  Say 'next' for Topic 9: Database Replication")
print("=" * 60)
