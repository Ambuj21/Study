"""
System Design Topic 7 - Caching: Python Simulations

Demonstrates:
- LRU Cache implementation from scratch
- Cache-Aside pattern simulation
- Write-Through vs Write-Behind comparison
- Cache stampede (thundering herd) simulation + solutions
- Cache hit rate vs size analysis
- TTL jitter for preventing mass expiration

Usage:
    python code.py
"""
import time
import random
import threading
import hashlib
from collections import OrderedDict
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed


# ================================================================
# 1. LRU CACHE — Built from Scratch
# ================================================================

print("=" * 60)
print("  1. LRU CACHE — Implementation & Demo")
print("=" * 60)


class LRUCache:
    """Least Recently Used cache with O(1) get/set."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: str):
        if key in self.cache:
            self.cache.move_to_end(key)  # Mark as recently used
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def set(self, key: str, value, ttl: float = None):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            evicted_key, _ = self.cache.popitem(last=False)  # Remove LRU
            return evicted_key
        return None

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total * 100 if total > 0 else 0

    def __len__(self):
        return len(self.cache)


# Demo LRU behavior
print(f"\n  --- LRU Cache (capacity=3) ---")
cache = LRUCache(capacity=3)

operations = [
    ("SET", "A", 1),
    ("SET", "B", 2),
    ("SET", "C", 3),
    ("GET", "A", None),     # A is accessed → becomes most recent
    ("SET", "D", 4),        # Cache full → evicts B (least recently used, not A!)
    ("GET", "B", None),     # B was evicted → MISS
    ("GET", "A", None),     # A is still there → HIT
    ("SET", "E", 5),        # Evicts C
]

for op, key, value in operations:
    if op == "SET":
        evicted = cache.set(key, value)
        state = list(cache.cache.keys())
        evict_str = f" (evicted {evicted})" if evicted else ""
        print(f"    SET {key}={value}{evict_str:20s} → Cache: {state}")
    else:
        result = cache.get(key)
        state = list(cache.cache.keys())
        status = f"HIT ({result})" if result is not None else "MISS"
        print(f"    GET {key} → {status:20s} → Cache: {state}")

print()


# ================================================================
# 2. CACHE-ASIDE PATTERN — Full Simulation
# ================================================================

print("=" * 60)
print("  2. CACHE-ASIDE PATTERN — With Simulated Database")
print("=" * 60)


class SimulatedDatabase:
    """Simulates a slow database."""

    def __init__(self):
        self.data = {f"user:{i}": {"name": f"User_{i}", "score": random.randint(1, 100)}
                     for i in range(1000)}
        self.query_count = 0
        self.latency_ms = 10  # Simulated DB latency

    def get(self, key: str) -> dict | None:
        self.query_count += 1
        time.sleep(self.latency_ms / 1000)  # Simulate slow DB
        return self.data.get(key)

    def update(self, key: str, value: dict):
        self.query_count += 1
        time.sleep(self.latency_ms / 1000)
        self.data[key] = value


class CacheAsideApp:
    """Application using cache-aside pattern."""

    def __init__(self, cache_capacity: int = 100):
        self.cache = LRUCache(cache_capacity)
        self.db = SimulatedDatabase()

    def get_user(self, user_id: int) -> dict:
        key = f"user:{user_id}"

        # Step 1: Check cache
        cached = self.cache.get(key)
        if cached is not None:
            return cached  # Cache HIT

        # Step 2: Cache miss — fetch from DB
        data = self.db.get(key)

        # Step 3: Populate cache
        if data:
            self.cache.set(key, data)

        return data

    def update_user(self, user_id: int, new_data: dict):
        key = f"user:{user_id}"
        # Write to DB
        self.db.update(key, new_data)
        # Invalidate cache (delete-on-write)
        if key in self.cache.cache:
            del self.cache.cache[key]


app = CacheAsideApp(cache_capacity=50)

# Simulate real traffic — Zipf distribution (popular users accessed more)
print(f"\n  --- Simulating 1,000 reads (Zipf distribution) ---")
start = time.perf_counter()

for _ in range(1000):
    user_id = min(int(random.paretovariate(1.2)), 999)
    app.get_user(user_id)

elapsed = (time.perf_counter() - start) * 1000

print(f"    Cache capacity:  50 items")
print(f"    Total requests:  1,000")
print(f"    Cache hits:      {app.cache.hits:,}")
print(f"    Cache misses:    {app.cache.misses:,}")
print(f"    Hit rate:        {app.cache.hit_rate:.1f}%")
print(f"    DB queries:      {app.db.query_count:,} (only on misses)")
print(f"    Total time:      {elapsed:.0f}ms")
print(f"    Without cache:   ~{1000 * 10:.0f}ms (10ms × 1000 queries)")
print(f"    Speedup:         {(1000 * 10) / elapsed:.1f}x faster!")

# Demo invalidation
print(f"\n  --- Write Invalidation Demo ---")
app2 = CacheAsideApp(cache_capacity=50)

# Read user (populates cache)
user = app2.get_user(1)
print(f"    Read user:1 → {user} (from DB, cached)")

# Read again (from cache)
user = app2.get_user(1)
print(f"    Read user:1 → {user} (from CACHE)")

# Update (invalidates cache)
app2.update_user(1, {"name": "User_1_UPDATED", "score": 999})
print(f"    Updated user:1 → cache INVALIDATED")

# Read again (cache miss, gets fresh data)
user = app2.get_user(1)
print(f"    Read user:1 → {user} (from DB, fresh!)")

print()


# ================================================================
# 3. WRITE-THROUGH vs WRITE-BEHIND COMPARISON
# ================================================================

print("=" * 60)
print("  3. WRITE-THROUGH vs WRITE-BEHIND — Speed Comparison")
print("=" * 60)


def simulate_write_through(num_writes: int, db_latency_ms: float = 10):
    """Write to cache AND DB synchronously."""
    start = time.perf_counter()
    for i in range(num_writes):
        # Write to cache (fast)
        time.sleep(0.0001)  # 0.1ms cache write
        # Write to DB (slow, synchronous)
        time.sleep(db_latency_ms / 1000)
    return (time.perf_counter() - start) * 1000


def simulate_write_behind(num_writes: int, db_latency_ms: float = 10, batch_size: int = 50):
    """Write to cache immediately, batch write to DB async."""
    start = time.perf_counter()
    buffer = []
    for i in range(num_writes):
        # Write to cache (fast)
        time.sleep(0.0001)  # 0.1ms cache write
        buffer.append(i)

        # Batch flush to DB
        if len(buffer) >= batch_size:
            time.sleep(db_latency_ms / 1000)  # One DB write for whole batch
            buffer.clear()

    # Flush remaining
    if buffer:
        time.sleep(db_latency_ms / 1000)

    return (time.perf_counter() - start) * 1000


num_writes = 200

wt_time = simulate_write_through(num_writes)
wb_time = simulate_write_behind(num_writes, batch_size=50)

print(f"\n  {num_writes} writes:")
print(f"    Write-Through: {wt_time:,.0f}ms ({wt_time/num_writes:.1f}ms per write)")
print(f"    Write-Behind:  {wb_time:,.0f}ms ({wb_time/num_writes:.1f}ms per write)")
print(f"    Write-Behind is {wt_time/wb_time:.1f}x faster!")
print(f"")
print(f"    Write-Through: Consistent but SLOW (each write waits for DB)")
print(f"    Write-Behind:  FAST but risky (data loss if cache crashes)")

print()


# ================================================================
# 4. CACHE STAMPEDE — Problem & Solutions
# ================================================================

print("=" * 60)
print("  4. CACHE STAMPEDE — Thundering Herd Problem")
print("=" * 60)


class StampedeDemo:
    """Demonstrates the thundering herd problem."""

    def __init__(self):
        self.db_queries = 0
        self.lock = threading.Lock()
        self.cache = {}
        self.fetch_lock = threading.Lock()

    def db_query(self, key: str) -> str:
        """Simulate expensive DB query."""
        with self.lock:
            self.db_queries += 1
        time.sleep(0.05)  # 50ms DB query
        return f"data_for_{key}"

    def get_no_protection(self, key: str) -> str:
        """No stampede protection — every miss hits DB."""
        if key in self.cache:
            return self.cache[key]
        # Cache miss — EVERYONE hits DB
        value = self.db_query(key)
        self.cache[key] = value
        return value

    def get_with_lock(self, key: str) -> str:
        """With lock — only ONE request hits DB."""
        if key in self.cache:
            return self.cache[key]

        with self.fetch_lock:  # Only one thread enters
            # Double-check after acquiring lock
            if key in self.cache:
                return self.cache[key]

            value = self.db_query(key)
            self.cache[key] = value
            return value


# Scenario: Cache expires, 100 concurrent requests hit same key
NUM_CONCURRENT = 100

# Without protection
demo1 = StampedeDemo()
with ThreadPoolExecutor(max_workers=NUM_CONCURRENT) as pool:
    futures = [pool.submit(demo1.get_no_protection, "popular_key") for _ in range(NUM_CONCURRENT)]
    for f in as_completed(futures):
        f.result()

print(f"\n  {NUM_CONCURRENT} concurrent requests for same expired key:")
print(f"    WITHOUT protection: {demo1.db_queries} DB queries  (should be 1!)")

# With lock protection
demo2 = StampedeDemo()
with ThreadPoolExecutor(max_workers=NUM_CONCURRENT) as pool:
    futures = [pool.submit(demo2.get_with_lock, "popular_key") for _ in range(NUM_CONCURRENT)]
    for f in as_completed(futures):
        f.result()

print(f"    WITH lock:          {demo2.db_queries} DB query   (only 1 hits DB!)")
print(f"    DB load reduced by {(1 - demo2.db_queries/demo1.db_queries)*100:.0f}%!")

print()


# ================================================================
# 5. TTL JITTER — Preventing Mass Expiration
# ================================================================

print("=" * 60)
print("  5. TTL JITTER — Preventing Mass Expiration")
print("=" * 60)


def simulate_expirations(num_keys: int, base_ttl: float, jitter_pct: float = 0):
    """Simulate when cache keys expire."""
    expirations_per_second = {}

    for _ in range(num_keys):
        if jitter_pct > 0:
            jitter = random.uniform(-jitter_pct, jitter_pct) * base_ttl
            ttl = base_ttl + jitter
        else:
            ttl = base_ttl

        expire_sec = int(ttl)
        expirations_per_second[expire_sec] = expirations_per_second.get(expire_sec, 0) + 1

    return expirations_per_second


print(f"\n  1,000 cache keys with TTL=300s")

# Without jitter
no_jitter = simulate_expirations(1000, 300, jitter_pct=0)
print(f"\n  WITHOUT jitter:")
for sec, count in sorted(no_jitter.items()):
    bar = "█" * min(count // 10, 50)
    print(f"    t={sec}s: {count:>5} keys expire {bar}")
print(f"    ALL 1,000 keys expire at SAME time → STAMPEDE!")

# With 20% jitter
with_jitter = simulate_expirations(1000, 300, jitter_pct=0.2)
print(f"\n  WITH 20% jitter (TTL=240-360s):")
for sec in sorted(with_jitter.keys()):
    count = with_jitter[sec]
    bar = "█" * min(count // 2, 50)
    if count > 5:
        print(f"    t={sec}s: {count:>5} keys expire {bar}")
print(f"    Keys expire GRADUALLY — no stampede!")

print()


# ================================================================
# 6. CACHE SIZE vs HIT RATE — Finding the Sweet Spot
# ================================================================

print("=" * 60)
print("  6. CACHE SIZE vs HIT RATE — The 80/20 Rule")
print("=" * 60)


def simulate_hit_rate(total_items: int, cache_size: int, num_requests: int = 10000):
    """Simulate cache hit rate with Zipf-distributed access."""
    cache = LRUCache(cache_size)
    db = {}

    for i in range(total_items):
        db[f"item:{i}"] = f"data_{i}"

    for _ in range(num_requests):
        # Zipf: popular items accessed much more
        item_idx = min(int(random.paretovariate(1.3)), total_items - 1)
        key = f"item:{item_idx}"

        if cache.get(key) is None:
            cache.set(key, db[key])

    return cache.hit_rate


total_items = 10000
print(f"\n  {total_items:,} unique items, 10,000 requests (Zipf distribution)")
print(f"\n  {'Cache Size':>12} {'% of Data':>10} {'Hit Rate':>10} {'Visualization'}")
print(f"  {'─'*12} {'─'*10} {'─'*10} {'─'*30}")

for cache_pct in [1, 2, 5, 10, 20, 30, 50, 80, 100]:
    cache_size = int(total_items * cache_pct / 100)
    if cache_size < 1:
        cache_size = 1
    hit_rate = simulate_hit_rate(total_items, cache_size)
    bar_full = int(hit_rate / 2)
    bar = "█" * bar_full + "░" * (50 - bar_full)
    print(f"  {cache_size:>12,} {cache_pct:>9}% {hit_rate:>9.1f}% {bar}")

print(f"""
  KEY INSIGHTS:
  ├── Caching just 5% of data → ~80% hit rate!
  ├── Caching 20% of data → ~95%+ hit rate
  ├── Beyond 30%, diminishing returns
  └── The 80/20 rule works because of Zipf distribution
      (a few items are MUCH more popular than the rest)""")


print("\n" + "=" * 60)
print("  System Design Topic 7 Complete!")
print("  Say 'next' for Topic 8: Databases Deep Dive")
print("=" * 60)
