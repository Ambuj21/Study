"""
System Design Topic 12 - API Design: Python Simulations

Demonstrates:
- REST API simulation with proper status codes and responses
- GraphQL vs REST data fetching comparison
- Pagination strategies (offset vs cursor)
- Rate limiting with Token Bucket algorithm
- API response time comparison (JSON vs binary)

Usage:
    python code.py
"""
import time
import json
import random
import hashlib
import base64
from dataclasses import dataclass, field
from collections import defaultdict


# ================================================================
# 1. REST API SIMULATION — Clean Design
# ================================================================

print("=" * 60)
print("  1. REST API — Clean Design & Status Codes")
print("=" * 60)


class MockRESTAPI:
    """Simulates a well-designed REST API."""

    def __init__(self):
        self.users = {
            1: {"id": 1, "name": "Alice", "email": "alice@mail.com", "age": 28},
            2: {"id": 2, "name": "Bob", "email": "bob@mail.com", "age": 32},
            3: {"id": 3, "name": "Charlie", "email": "charlie@mail.com", "age": 25},
        }
        self.next_id = 4

    def handle(self, method: str, path: str, body: dict = None) -> tuple[int, dict]:
        """Route and handle REST requests."""
        parts = path.strip("/").split("/")

        # GET /users
        if method == "GET" and parts == ["users"]:
            return 200, {"data": list(self.users.values()), "count": len(self.users)}

        # GET /users/:id
        if method == "GET" and len(parts) == 2 and parts[0] == "users":
            user_id = int(parts[1])
            if user_id in self.users:
                return 200, {"data": self.users[user_id]}
            return 404, {"error": {"code": "NOT_FOUND", "message": f"User {user_id} not found"}}

        # POST /users
        if method == "POST" and parts == ["users"]:
            if not body or "name" not in body:
                return 400, {"error": {"code": "VALIDATION_ERROR",
                                       "message": "Name is required",
                                       "details": [{"field": "name", "message": "Required"}]}}
            if any(u["email"] == body.get("email") for u in self.users.values()):
                return 409, {"error": {"code": "CONFLICT", "message": "Email already exists"}}

            user = {"id": self.next_id, **body}
            self.users[self.next_id] = user
            self.next_id += 1
            return 201, {"data": user, "message": "User created"}

        # DELETE /users/:id
        if method == "DELETE" and len(parts) == 2 and parts[0] == "users":
            user_id = int(parts[1])
            if user_id in self.users:
                del self.users[user_id]
                return 204, {}
            return 404, {"error": {"code": "NOT_FOUND", "message": f"User {user_id} not found"}}

        return 400, {"error": {"code": "BAD_REQUEST", "message": "Unknown endpoint"}}


api = MockRESTAPI()

requests = [
    ("GET",    "/users",     None,                                    "List all users"),
    ("GET",    "/users/1",   None,                                    "Get user 1"),
    ("GET",    "/users/99",  None,                                    "Get nonexistent user"),
    ("POST",   "/users",     {"name": "Diana", "email": "d@mail.com"}, "Create user"),
    ("POST",   "/users",     {},                                       "Create without name (error)"),
    ("POST",   "/users",     {"name": "Dupe", "email": "d@mail.com"},  "Duplicate email (conflict)"),
    ("DELETE", "/users/2",   None,                                    "Delete user 2"),
    ("DELETE", "/users/99",  None,                                    "Delete nonexistent"),
]

print(f"\n  {'Method':<8} {'Path':<14} {'Status':>7} {'Description'}")
print(f"  {'─'*8} {'─'*14} {'─'*7} {'─'*30}")

for method, path, body, desc in requests:
    status, response = api.handle(method, path, body)
    emoji = "✅" if status < 300 else "⚠️" if status < 500 else "❌"
    print(f"  {method:<8} {path:<14} {emoji} {status:>4}  {desc}")

print()


# ================================================================
# 2. REST vs GRAPHQL — Data Fetching Comparison
# ================================================================

print("=" * 60)
print("  2. REST vs GRAPHQL — Number of Requests")
print("=" * 60)


# Scenario: Display a user profile page with posts and comments
def rest_fetch_profile():
    """REST: Multiple requests for a profile page."""
    requests_made = []

    # Request 1: Get user
    requests_made.append("GET /users/123")
    user = {"id": 123, "name": "Alice", "avatar": "alice.jpg", "bio": "...",
            "email": "...", "phone": "...", "address": "...", "settings": "..."}

    # Request 2: Get user's posts
    requests_made.append("GET /users/123/posts?limit=5")
    posts = [{"id": i, "title": f"Post {i}", "body": "...", "likes": random.randint(0, 100),
              "created_at": "...", "updated_at": "...", "tags": "..."} for i in range(5)]

    # Request 3-7: Get comments for each post
    for post in posts:
        requests_made.append(f"GET /posts/{post['id']}/comments?limit=3")

    # Total data transferred includes unused fields
    data_fields = 8 + (7 * 5) + (5 * 3 * 4)  # user + posts + comments
    useful_fields = 2 + (2 * 5) + (5 * 3 * 2)  # only what we display

    return requests_made, data_fields, useful_fields


def graphql_fetch_profile():
    """GraphQL: Single request for the same data."""
    requests_made = ["POST /graphql"]

    # Single query gets exactly what we need
    # query { user(id:123) { name, avatar, posts(last:5) { title, likes, comments(first:3) { text, author } } } }

    data_fields = 2 + (2 * 5) + (5 * 3 * 2)  # exactly what we asked for
    useful_fields = data_fields  # 100% utilized!

    return requests_made, data_fields, useful_fields


rest_reqs, rest_total, rest_useful = rest_fetch_profile()
gql_reqs, gql_total, gql_useful = graphql_fetch_profile()

print(f"\n  Scenario: User profile page (user + 5 posts + comments)")
print(f"\n  {'Metric':<25} {'REST':>10} {'GraphQL':>10}")
print(f"  {'─'*25} {'─'*10} {'─'*10}")
print(f"  {'HTTP requests':<25} {len(rest_reqs):>10} {len(gql_reqs):>10}")
print(f"  {'Total fields returned':<25} {rest_total:>10} {gql_total:>10}")
print(f"  {'Useful fields':<25} {rest_useful:>10} {gql_useful:>10}")
print(f"  {'Data efficiency':<25} {rest_useful/rest_total*100:>9.0f}% {gql_useful/gql_total*100:>9.0f}%")

print(f"\n  REST requests made:")
for r in rest_reqs:
    print(f"    {r}")

print(f"\n  GraphQL request:")
print(f"    POST /graphql (single request, exact fields)")
print(f"\n  GraphQL: {len(rest_reqs)}x fewer requests, 100% data efficiency!")

print()


# ================================================================
# 3. PAGINATION — Offset vs Cursor
# ================================================================

print("=" * 60)
print("  3. PAGINATION — Offset vs Cursor Performance")
print("=" * 60)

# Simulate a database with 1M records
DB_SIZE = 1_000_000
data = list(range(DB_SIZE))  # Simulated IDs


def offset_pagination(page: int, limit: int = 20) -> tuple[list, float]:
    """Offset-based: Skip N rows, take limit."""
    start = time.perf_counter()
    offset = (page - 1) * limit
    # Simulate scanning: DB must scan through `offset` rows to skip them
    _ = data[:offset]  # Simulated scan work
    results = data[offset:offset + limit]
    elapsed = (time.perf_counter() - start) * 1000
    return results, elapsed


def cursor_pagination(cursor: int, limit: int = 20) -> tuple[list, float]:
    """Cursor-based: Start after cursor, take limit."""
    start = time.perf_counter()
    # Uses index: jump directly to cursor position — O(log n)
    results = [x for x in data if x > cursor][:limit]
    elapsed = (time.perf_counter() - start) * 1000
    return results, elapsed


print(f"\n  Database: {DB_SIZE:,} records, fetching 20 per page")
print(f"\n  {'Page/Position':<20} {'Offset Time':>14} {'Cursor Time':>14} {'Winner':<10}")
print(f"  {'─'*20} {'─'*14} {'─'*14} {'─'*10}")

test_pages = [1, 100, 1000, 10000, 50000]
for page in test_pages:
    cursor_pos = (page - 1) * 20
    _, offset_time = offset_pagination(page)
    _, cursor_time = cursor_pagination(cursor_pos)
    winner = "Cursor!" if cursor_time < offset_time else "Offset"
    print(f"  Page {page:<14} {offset_time:>12.3f}ms {cursor_time:>12.3f}ms {winner:<10}")

print(f"""
  KEY INSIGHT:
    Offset: Gets SLOWER as you go deeper (must skip more rows)
    Cursor: CONSTANT speed regardless of position (uses index)

    Page 1 → Both fast
    Page 50,000 → Offset scans 1M rows, Cursor jumps directly!

    Use cursor-based pagination for: feeds, chat history, infinite scroll
    Use offset-based for: admin panels, small datasets""")

print()


# ================================================================
# 4. RATE LIMITING — Token Bucket Algorithm
# ================================================================

print("=" * 60)
print("  4. RATE LIMITING — Token Bucket Algorithm")
print("=" * 60)


class TokenBucket:
    """Token Bucket rate limiter."""

    def __init__(self, capacity: int, refill_rate: float):
        """
        capacity: max tokens in bucket
        refill_rate: tokens added per second
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.allowed = 0
        self.rejected = 0

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    def allow(self) -> tuple[bool, dict]:
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            self.allowed += 1
            return True, {
                "X-RateLimit-Limit": self.capacity,
                "X-RateLimit-Remaining": int(self.tokens),
            }
        else:
            self.rejected += 1
            return False, {
                "X-RateLimit-Limit": self.capacity,
                "X-RateLimit-Remaining": 0,
                "Retry-After": f"{1/self.refill_rate:.1f}s",
            }


# Simulate: 10 requests/sec limit, burst of 30 requests
limiter = TokenBucket(capacity=10, refill_rate=10)  # 10 tokens, refills 10/sec

print(f"\n  Rate limit: 10 requests/second (burst capacity: 10)")
print(f"\n  --- Burst: 15 rapid requests ---")

for i in range(15):
    allowed, headers = limiter.allow()
    status = f"✅ 200 OK (remaining: {headers['X-RateLimit-Remaining']})" if allowed \
             else f"❌ 429 Too Many Requests (retry after: {headers['Retry-After']})"
    print(f"    Request {i+1:>2}: {status}")

print(f"\n  --- Wait 1 second (bucket refills) ---")
time.sleep(1)

for i in range(5):
    allowed, headers = limiter.allow()
    status = f"✅ 200 OK (remaining: {headers['X-RateLimit-Remaining']})" if allowed \
             else f"❌ 429 (retry: {headers['Retry-After']})"
    print(f"    Request {i+16:>2}: {status}")

print(f"\n  Summary: {limiter.allowed} allowed, {limiter.rejected} rejected")

print()


# ================================================================
# 5. JSON vs BINARY — Response Size Comparison
# ================================================================

print("=" * 60)
print("  5. JSON vs BINARY — Protocol Efficiency")
print("=" * 60)

# Simulate the same data in JSON vs binary (protobuf-like)
users_data = [
    {"id": i, "name": f"User_{i}", "email": f"user{i}@company.com",
     "age": random.randint(18, 65), "active": True}
    for i in range(100)
]

# JSON size
json_bytes = len(json.dumps(users_data).encode())

# Simulated binary (Protocol Buffers are ~3-5x smaller)
# Binary: 4 bytes (id) + len(name) + len(email) + 1 byte (age) + 1 byte (active)
binary_bytes = sum(
    4 + len(u["name"]) + len(u["email"]) + 1 + 1
    for u in users_data
)

# Serialization speed
start = time.perf_counter()
for _ in range(1000):
    json.dumps(users_data)
json_time = (time.perf_counter() - start) * 1000

start = time.perf_counter()
for _ in range(1000):
    # Simulated binary serialization (struct-like packing)
    b = bytearray()
    for u in users_data:
        b.extend(u["id"].to_bytes(4, "big"))
        b.extend(u["name"].encode())
        b.extend(u["email"].encode())
binary_time = (time.perf_counter() - start) * 1000

print(f"\n  100 user records — JSON (REST) vs Binary (gRPC):")
print(f"\n  {'Metric':<25} {'JSON (REST)':>14} {'Binary (gRPC)':>14} {'Ratio':>8}")
print(f"  {'─'*25} {'─'*14} {'─'*14} {'─'*8}")
print(f"  {'Response size':<25} {json_bytes:>11,} B {binary_bytes:>11,} B {json_bytes/binary_bytes:>6.1f}x")
print(f"  {'Serialization (1K reps)':<25} {json_time:>12.1f}ms {binary_time:>12.1f}ms {json_time/binary_time:>6.1f}x")

print(f"""
  Binary (gRPC/Protobuf):
    {json_bytes/binary_bytes:.1f}x smaller payload → less bandwidth
    {json_time/binary_time:.1f}x faster serialization → less CPU
    Typed + code-generated → fewer bugs

  But JSON (REST):
    Human-readable (debug in browser!)
    No compilation step needed
    Universal support (every language, every tool)

  RULE: REST/JSON for external APIs, gRPC/Protobuf for internal services""")


# ================================================================
# 6. PROTOCOL SUMMARY
# ================================================================

print()
print("=" * 60)
print("  6. PROTOCOL COMPARISON — Quick Reference")
print("=" * 60)

print(f"""
  ┌────────────┬────────────────┬──────────────┬──────────────┐
  │  Protocol  │  Best For      │  Speed       │  Complexity  │
  ├────────────┼────────────────┼──────────────┼──────────────┤
  │  REST      │  Public APIs   │  Good        │  Low         │
  │            │  CRUD apps     │              │              │
  ├────────────┼────────────────┼──────────────┼──────────────┤
  │  GraphQL   │  Mobile apps   │  Good        │  Medium      │
  │            │  Nested data   │              │              │
  ├────────────┼────────────────┼──────────────┼──────────────┤
  │  gRPC      │  Microservices │  Fastest     │  Medium      │
  │            │  Internal APIs │  (binary)    │              │
  ├────────────┼────────────────┼──────────────┼──────────────┤
  │  WebSocket │  Real-time     │  Fastest     │  High        │
  │            │  Chat, gaming  │  (streaming) │              │
  └────────────┴────────────────┴──────────────┴──────────────┘

  Real-world combos:
    Stripe:     REST (external) + gRPC (internal)
    GitHub:     REST + GraphQL (both external)
    Slack:      REST + WebSocket (real-time messages)
    Netflix:    GraphQL (client-facing) + gRPC (internal)
""")


print("=" * 60)
print("  System Design Topic 12 Complete!")
print("  STAGE 2: Core Building Blocks — ALL DONE!")
print("  Say 'next' for Stage 3: Microservices Architecture")
print("=" * 60)
