"""
System Design Topic 10 - Database Sharding: Python Simulations

Demonstrates:
- Hash-based sharding with distribution analysis
- Range-based sharding with hotspot detection
- Cross-shard query simulation (scatter-gather)
- Resharding pain — data migration when adding shards
- Shard rebalancing visualization

Usage:
    python code.py
"""
import time
import random
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field


# ================================================================
# 1. HASH-BASED SHARDING — Distribution Analysis
# ================================================================

print("=" * 60)
print("  1. HASH-BASED SHARDING — Even Data Distribution")
print("=" * 60)


class HashSharder:
    """Hash-based sharding: HASH(key) % num_shards."""

    def __init__(self, num_shards: int):
        self.num_shards = num_shards
        self.shards = {i: [] for i in range(num_shards)}

    def get_shard(self, key: str) -> int:
        hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return hash_val % self.num_shards

    def insert(self, key: str, value: dict):
        shard_id = self.get_shard(key)
        self.shards[shard_id].append((key, value))
        return shard_id

    def query(self, key: str):
        shard_id = self.get_shard(key)
        for k, v in self.shards[shard_id]:
            if k == key:
                return v, shard_id
        return None, shard_id


# Insert 10,000 users across 4 shards
sharder = HashSharder(num_shards=4)
for i in range(10_000):
    sharder.insert(f"user:{i}", {"name": f"User_{i}", "email": f"user{i}@mail.com"})

print(f"\n  10,000 users across 4 shards (hash-based):")
print(f"\n  {'Shard':>8} {'Items':>8} {'Percent':>9} {'Distribution'}")
print(f"  {'─'*8} {'─'*8} {'─'*9} {'─'*30}")

for shard_id in range(4):
    count = len(sharder.shards[shard_id])
    pct = count / 10_000 * 100
    bar = "█" * int(pct / 2) + "░" * (25 - int(pct / 2))
    print(f"  Shard {shard_id} {count:>8} {pct:>8.1f}% {bar}")

# Query routing demo
print(f"\n  --- Query Routing ---")
test_users = ["user:42", "user:999", "user:5000", "user:7777"]
for user_key in test_users:
    value, shard = sharder.query(user_key)
    print(f"    {user_key} → Shard {shard} (deterministic!)")

print(f"\n  Hash-based: Near-perfect even distribution!")

print()


# ================================================================
# 2. RANGE-BASED SHARDING — Hotspot Problem
# ================================================================

print("=" * 60)
print("  2. RANGE-BASED SHARDING — The Hotspot Problem")
print("=" * 60)


class RangeSharder:
    """Range-based sharding: key range → shard."""

    def __init__(self, ranges: list[tuple[int, int]]):
        self.ranges = ranges  # [(start, end), ...]
        self.shards = {i: [] for i in range(len(ranges))}
        self.write_counts = {i: 0 for i in range(len(ranges))}

    def get_shard(self, key_id: int) -> int:
        for i, (start, end) in enumerate(self.ranges):
            if start <= key_id <= end:
                return i
        return len(self.ranges) - 1

    def insert(self, key_id: int, value: dict):
        shard_id = self.get_shard(key_id)
        self.shards[shard_id].append((key_id, value))
        self.write_counts[shard_id] += 1
        return shard_id


# 4 shards with equal ranges
range_sharder = RangeSharder([
    (1, 2_500_000),
    (2_500_001, 5_000_000),
    (5_000_001, 7_500_000),
    (7_500_001, 10_000_000),
])

# Simulate user registration (sequential IDs = ALL writes go to last shard!)
print(f"\n  --- Simulating 10,000 NEW user registrations ---")
print(f"  (User IDs are sequential: 9,990,001 to 10,000,000)")

for i in range(9_990_001, 10_000_001):
    range_sharder.insert(i, {"name": f"NewUser_{i}"})

print(f"\n  {'Shard':>8} {'Range':<25} {'Writes':>8} {'Status'}")
print(f"  {'─'*8} {'─'*25} {'─'*8} {'─'*15}")

for i, (start, end) in enumerate(range_sharder.ranges):
    writes = range_sharder.write_counts[i]
    status = "HOTSPOT!" if writes > 5000 else "idle" if writes == 0 else "normal"
    indicator = "🔥🔥🔥" if writes > 5000 else "✅" if writes == 0 else "⚠️"
    print(f"  Shard {i} {start:>10}-{end:<12} {writes:>8} {indicator} {status}")

print(f"\n  PROBLEM: All new users go to Shard 3 (hotspot!)")
print(f"  Shards 0-2 are idle while Shard 3 is overwhelmed.")
print(f"  This is why hash-based is usually better than range-based.")

print()


# ================================================================
# 3. CROSS-SHARD QUERY — Scatter-Gather
# ================================================================

print("=" * 60)
print("  3. CROSS-SHARD QUERY — Scatter-Gather Pattern")
print("=" * 60)


class ShardedDB:
    """Simulated sharded database with cross-shard query support."""

    def __init__(self, num_shards: int = 4):
        self.num_shards = num_shards
        self.shards = {i: [] for i in range(num_shards)}

    def insert(self, user_id: int, order: dict):
        shard = user_id % self.num_shards
        self.shards[shard].append({"user_id": user_id, **order})

    def single_shard_query(self, user_id: int) -> tuple[list, int]:
        """Query that hits ONE shard — FAST."""
        shard = user_id % self.num_shards
        results = [r for r in self.shards[shard] if r["user_id"] == user_id]
        return results, 1  # 1 shard queried

    def cross_shard_query(self, condition) -> tuple[list, int]:
        """Query that must scan ALL shards — SLOW."""
        all_results = []
        for shard_id in range(self.num_shards):
            local_results = [r for r in self.shards[shard_id] if condition(r)]
            all_results.extend(local_results)
        return all_results, self.num_shards  # All shards queried


# Populate with orders
db = ShardedDB(num_shards=4)
products = ["Laptop", "Phone", "Tablet", "Mouse", "Keyboard", "Monitor"]

for _ in range(10_000):
    user_id = random.randint(1, 1000)
    order = {
        "product": random.choice(products),
        "total": round(random.uniform(10, 2000), 2),
        "status": random.choice(["paid", "pending", "shipped"]),
    }
    db.insert(user_id, order)

# Single-shard query (fast!)
print(f"\n  --- Single-Shard Query (by user_id) ---")
start = time.perf_counter()
results, shards_hit = db.single_shard_query(42)
single_time = (time.perf_counter() - start) * 1000
print(f"    Query: 'Get all orders for user 42'")
print(f"    Results: {len(results)} orders found")
print(f"    Shards queried: {shards_hit} / {db.num_shards}")
print(f"    Time: {single_time:.3f}ms")

# Cross-shard query (slow!)
print(f"\n  --- Cross-Shard Query (by product) ---")
start = time.perf_counter()
results, shards_hit = db.cross_shard_query(
    lambda r: r["product"] == "Laptop" and r["total"] > 500
)
cross_time = (time.perf_counter() - start) * 1000
print(f"    Query: 'Find all Laptop orders over $500'")
print(f"    Results: {len(results)} orders found")
print(f"    Shards queried: {shards_hit} / {db.num_shards} (ALL shards!)")
print(f"    Time: {cross_time:.3f}ms")

print(f"\n    Cross-shard query is {cross_time/single_time:.1f}x slower!")
print(f"    LESSON: Design shard key so most queries hit ONE shard")

print()


# ================================================================
# 4. RESHARDING — The Pain of Adding Shards
# ================================================================

print("=" * 60)
print("  4. RESHARDING — Adding a 5th Shard to 4 Existing")
print("=" * 60)

NUM_KEYS = 10_000

# Original: 4 shards
original_mapping = {}
for i in range(NUM_KEYS):
    key = f"user:{i}"
    hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
    original_mapping[key] = hash_val % 4

# New: 5 shards
new_mapping = {}
for i in range(NUM_KEYS):
    key = f"user:{i}"
    hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
    new_mapping[key] = hash_val % 5

# Count how many keys moved
moved = sum(1 for k in original_mapping if original_mapping[k] != new_mapping[k])
pct_moved = moved / NUM_KEYS * 100

print(f"\n  {NUM_KEYS:,} keys, going from 4 shards to 5 shards:")
print(f"    Keys that STAY on same shard: {NUM_KEYS - moved:,} ({100 - pct_moved:.1f}%)")
print(f"    Keys that must MOVE:          {moved:,} ({pct_moved:.1f}%)")

# Show migration per shard
print(f"\n  Migration details:")
print(f"  {'From Shard':>12} {'Keys Out':>10} {'Keys In':>10} {'Net Change':>12}")
print(f"  {'─'*12} {'─'*10} {'─'*10} {'─'*12}")

for shard in range(5):
    was_here = sum(1 for k in original_mapping if original_mapping[k] == shard) if shard < 4 else 0
    now_here = sum(1 for k in new_mapping if new_mapping[k] == shard)
    stayed = sum(1 for k in new_mapping if new_mapping[k] == shard and original_mapping.get(k) == shard)
    keys_out = was_here - stayed
    keys_in = now_here - stayed
    net = keys_in - keys_out
    print(f"  Shard {shard:>4} {keys_out:>10} {keys_in:>10} {net:>+12}")

print(f"""
  RESHARDING PAIN:
    {pct_moved:.0f}% of data must be copied between servers!
    During migration:
      - Must handle reads/writes to BOTH old and new locations
      - Risk of data inconsistency
      - Takes hours/days for large datasets

  SOLUTION: Consistent Hashing (Topic 14)
    Adding 1 shard to 4 → only ~{100/5:.0f}% of data moves (not {pct_moved:.0f}%!)""")

print()


# ================================================================
# 5. SHARD SCALING — Capacity Planning
# ================================================================

print("=" * 60)
print("  5. SHARD CAPACITY PLANNING")
print("=" * 60)


def plan_sharding(
    total_data_tb: float,
    write_qps: int,
    read_qps: int,
    max_data_per_shard_tb: float = 5.0,
    max_write_qps_per_shard: int = 5000,
    max_read_qps_per_shard: int = 10000,
):
    """Calculate how many shards are needed."""
    shards_for_data = max(1, int(total_data_tb / max_data_per_shard_tb) + 1)
    shards_for_writes = max(1, int(write_qps / max_write_qps_per_shard) + 1)
    shards_for_reads = max(1, int(read_qps / max_read_qps_per_shard) + 1)

    shards_needed = max(shards_for_data, shards_for_writes, shards_for_reads)

    # With replicas (3 per shard)
    total_servers = shards_needed * 4  # 1 primary + 3 replicas per shard

    return {
        "shards_for_data": shards_for_data,
        "shards_for_writes": shards_for_writes,
        "shards_for_reads": shards_for_reads,
        "shards_needed": shards_needed,
        "total_servers": total_servers,
    }


scenarios = [
    ("Small Startup",        0.5,     500,    5_000),
    ("Growing App",          5,     3_000,   30_000),
    ("Instagram-scale",     50,    20_000,  200_000),
    ("Twitter-scale",      200,    50_000,  500_000),
]

print(f"\n  {'Scenario':<20} {'Data':>6} {'W-QPS':>8} {'R-QPS':>8} {'Shards':>8} {'Servers':>9} {'Bottleneck':<12}")
print(f"  {'─'*20} {'─'*6} {'─'*8} {'─'*8} {'─'*8} {'─'*9} {'─'*12}")

for name, data, wqps, rqps in scenarios:
    result = plan_sharding(data, wqps, rqps)
    bottleneck = "Data" if result["shards_for_data"] == result["shards_needed"] else \
                 "Writes" if result["shards_for_writes"] == result["shards_needed"] else "Reads"
    print(f"  {name:<20} {data:>4} TB {wqps:>7,} {rqps:>7,} "
          f"{result['shards_needed']:>8} {result['total_servers']:>9} {bottleneck:<12}")

print(f"""
  NOTE: "Servers" = shards × 4 (1 primary + 3 replicas each)

  SCALING ORDER (try before sharding!):
    1. Add caching (Redis)         → Reduces reads by 80%
    2. Add read replicas           → Scales reads linearly
    3. Vertical scaling            → Bigger machines
    4. Shard ONLY when necessary   → Last resort!""")


# ================================================================
# 6. TRY BEFORE SHARDING — Cost Comparison
# ================================================================

print()
print("=" * 60)
print("  6. BEFORE SHARDING — Simpler Alternatives")
print("=" * 60)

print(f"""
  SCENARIO: Database has 10,000 reads/sec, struggling

  OPTION 1: Add Redis Cache (80% hit rate)
    DB load: 10,000 → 2,000 reads/sec (80% reduction!)
    Cost: 1 Redis server (~$200/month)
    Complexity: Low

  OPTION 2: Add 2 Read Replicas
    DB read capacity: 10,000 → 30,000 reads/sec (3x!)
    Cost: 2 more DB servers (~$800/month)
    Complexity: Low

  OPTION 3: Vertical Scaling (2x bigger machine)
    DB capacity: 10,000 → 20,000 reads/sec
    Cost: ~$500/month more
    Complexity: Zero (just resize)

  OPTION 4: Shard into 4 shards
    DB capacity: 10,000 → 40,000 reads/sec
    Cost: 16 servers (4 shards × 4 replicas) = ~$3,200/month
    Complexity: VERY HIGH (code changes, routing, cross-shard queries)

  VERDICT: Options 1+2 solve the problem at 1/3 the cost
           and 1/10 the complexity of sharding!""")


print("\n" + "=" * 60)
print("  System Design Topic 10 Complete!")
print("  Say 'next' for Topic 11: Message Queues")
print("=" * 60)
