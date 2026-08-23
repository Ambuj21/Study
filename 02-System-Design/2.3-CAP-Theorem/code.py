"""
System Design Topic 3 - CAP Theorem: Python Simulations

Demonstrates:
- CP vs AP behavior during network partitions
- Consistency models (strong, eventual, read-your-writes)
- Conflict resolution strategies (last-write-wins, vector clocks)
- Quorum-based consistency (tunable consistency)

Usage:
    python code.py
"""
import time
import random
import threading
from dataclasses import dataclass, field
from copy import deepcopy


# ================================================================
# 1. SIMULATING A NETWORK PARTITION
# ================================================================

print("=" * 60)
print("  1. NETWORK PARTITION — What Actually Happens")
print("=" * 60)


class NetworkSimulator:
    """Simulates network connectivity between nodes."""

    def __init__(self):
        self.partitioned = False

    def is_reachable(self, from_node: str, to_node: str) -> bool:
        if self.partitioned:
            # NYC nodes can't reach London nodes
            nyc = from_node.startswith("NYC")
            london = to_node.startswith("LON")
            if (nyc and london) or (not nyc and not london is False):
                return from_node.startswith("NYC") == to_node.startswith("NYC")
        return True


@dataclass
class Replica:
    name: str
    data: dict = field(default_factory=dict)
    write_log: list = field(default_factory=list)

    def local_write(self, key: str, value, timestamp: float):
        self.data[key] = {"value": value, "timestamp": timestamp}
        self.write_log.append({"key": key, "value": value, "time": timestamp})

    def local_read(self, key: str):
        entry = self.data.get(key)
        return entry["value"] if entry else None


# Create two replicas in different data centers
nyc_replica = Replica("NYC-Server")
london_replica = Replica("LON-Server")
network = NetworkSimulator()

print("\n  --- Normal Operation (no partition) ---")
nyc_replica.local_write("balance", 1000, time.time())
london_replica.data = deepcopy(nyc_replica.data)  # Sync
print(f"    NYC write: balance = 1000")
print(f"    NYC read:    balance = {nyc_replica.local_read('balance')}")
print(f"    London read: balance = {london_replica.local_read('balance')}")
print(f"    Both consistent!")

print("\n  --- Network Partition Happens! ---")
network.partitioned = True
print(f"    Cable between NYC and London is CUT!")

# Write happens on NYC side during partition
nyc_replica.local_write("balance", 900, time.time())
print(f"    NYC writes:  balance = 900 (Alice transfers $100)")
print(f"    NYC read:    balance = {nyc_replica.local_read('balance')}")
print(f"    London read: balance = {london_replica.local_read('balance')}")
print(f"    INCONSISTENT! London still shows old value!")

print()


# ================================================================
# 2. CP SYSTEM — Consistency + Partition Tolerance
# ================================================================

print("=" * 60)
print("  2. CP SYSTEM — Blocks during partition for consistency")
print("=" * 60)


class CPDatabase:
    """CP system: Ensures consistency, sacrifices availability during partition."""

    def __init__(self):
        self.primary = Replica("PRIMARY")
        self.replicas = [Replica("REPLICA-1"), Replica("REPLICA-2")]
        self.partitioned = False

    def write(self, key: str, value) -> tuple[bool, str]:
        ts = time.time()
        self.primary.local_write(key, value, ts)

        if self.partitioned:
            # Can't reach replicas — BLOCK the write!
            # Rollback primary
            self.primary.data.pop(key, None)
            return False, "WRITE BLOCKED: Cannot reach replicas (partition)"

        # Sync write — wait for ALL replicas
        for replica in self.replicas:
            replica.local_write(key, value, ts)

        return True, "Write successful (all replicas synced)"

    def read(self, key: str) -> tuple[bool, str]:
        if self.partitioned:
            return False, "READ BLOCKED: Cannot verify consistency"

        value = self.primary.local_read(key)
        return True, f"value = {value}"


cp_db = CPDatabase()

print("\n  --- Normal operation ---")
ok, msg = cp_db.write("user:alice:balance", 1000)
print(f"    Write balance=1000: {msg}")
ok, msg = cp_db.read("user:alice:balance")
print(f"    Read balance: {msg}")

print("\n  --- During partition ---")
cp_db.partitioned = True
ok, msg = cp_db.write("user:alice:balance", 900)
print(f"    Write balance=900: {msg}")
ok, msg = cp_db.read("user:alice:balance")
print(f"    Read balance: {msg}")
print(f"    CP BEHAVIOR: Refuses to serve rather than give wrong data!")

print()


# ================================================================
# 3. AP SYSTEM — Availability + Partition Tolerance
# ================================================================

print("=" * 60)
print("  3. AP SYSTEM — Always responds, even with stale data")
print("=" * 60)


class APDatabase:
    """AP system: Always available, eventually consistent."""

    def __init__(self):
        self.nodes = {
            "NYC": Replica("NYC"),
            "LON": Replica("LON"),
        }
        self.partitioned = False
        self.pending_sync = []  # Writes to sync after partition heals

    def write(self, node_name: str, key: str, value) -> str:
        ts = time.time()
        self.nodes[node_name].local_write(key, value, ts)

        if self.partitioned:
            # Save for later sync
            self.pending_sync.append({"node": node_name, "key": key, "value": value, "time": ts})
            return f"Write accepted locally on {node_name} (will sync later)"

        # Normal: replicate to all nodes
        for name, node in self.nodes.items():
            if name != node_name:
                node.local_write(key, value, ts)

        return f"Write replicated to all nodes"

    def read(self, node_name: str, key: str) -> str:
        value = self.nodes[node_name].local_read(key)
        return f"value = {value} (from {node_name})"

    def heal_partition(self) -> str:
        """Resolve conflicts after partition heals using last-write-wins."""
        self.partitioned = False
        conflicts_resolved = 0

        # Collect all data from all nodes, keep latest timestamp
        merged = {}
        for name, node in self.nodes.items():
            for key, entry in node.data.items():
                if key not in merged or entry["timestamp"] > merged[key]["timestamp"]:
                    merged[key] = entry

        # Apply merged data to all nodes
        for name, node in self.nodes.items():
            node.data = {k: deepcopy(v) for k, v in merged.items()}
            conflicts_resolved += 1

        self.pending_sync.clear()
        return f"Partition healed! Synced {len(merged)} keys across {conflicts_resolved} nodes"


ap_db = APDatabase()

print("\n  --- Normal operation ---")
msg = ap_db.write("NYC", "likes:post123", 42)
print(f"    Write likes=42: {msg}")
print(f"    Read from NYC: {ap_db.read('NYC', 'likes:post123')}")
print(f"    Read from LON: {ap_db.read('LON', 'likes:post123')}")

print("\n  --- During partition ---")
ap_db.partitioned = True
msg = ap_db.write("NYC", "likes:post123", 50)
print(f"    NYC writes likes=50: {msg}")
msg = ap_db.write("LON", "likes:post123", 45)
print(f"    LON writes likes=45: {msg}")
print(f"    Read from NYC: {ap_db.read('NYC', 'likes:post123')}")
print(f"    Read from LON: {ap_db.read('LON', 'likes:post123')}")
print(f"    AP BEHAVIOR: Both respond, but show DIFFERENT values!")

print("\n  --- Partition heals ---")
msg = ap_db.heal_partition()
print(f"    {msg}")
print(f"    Read from NYC: {ap_db.read('NYC', 'likes:post123')}")
print(f"    Read from LON: {ap_db.read('LON', 'likes:post123')}")
print(f"    Consistent again! (Last-write-wins resolved the conflict)")

print()


# ================================================================
# 4. CONSISTENCY MODELS COMPARISON
# ================================================================

print("=" * 60)
print("  4. CONSISTENCY MODELS — Strong vs Eventual")
print("=" * 60)


class StrongConsistencyDB:
    """Every read returns the latest write. Slow but safe."""

    def __init__(self, num_replicas: int = 3):
        self.replicas = [Replica(f"R{i}") for i in range(num_replicas)]

    def write(self, key: str, value) -> float:
        start = time.perf_counter()
        ts = time.time()
        # Must write to ALL replicas synchronously
        for r in self.replicas:
            r.local_write(key, value, ts)
            time.sleep(0.002)  # Simulate network latency per replica
        latency = (time.perf_counter() - start) * 1000
        return latency

    def read(self, key: str):
        return self.replicas[0].local_read(key)


class EventualConsistencyDB:
    """Write locally, replicate async. Fast but might be stale."""

    def __init__(self, num_replicas: int = 3):
        self.replicas = [Replica(f"R{i}") for i in range(num_replicas)]

    def write(self, key: str, value) -> float:
        start = time.perf_counter()
        ts = time.time()
        # Write to ONE replica (local), return immediately
        self.replicas[0].local_write(key, value, ts)
        latency = (time.perf_counter() - start) * 1000

        # Replicate in background (async simulation)
        def replicate():
            time.sleep(0.01)  # Simulated delay
            for r in self.replicas[1:]:
                r.local_write(key, value, ts)

        threading.Thread(target=replicate, daemon=True).start()

        return latency

    def read(self, key: str, replica_idx: int = 0):
        return self.replicas[replica_idx].local_read(key)


# Compare latencies
strong_db = StrongConsistencyDB(num_replicas=3)
eventual_db = EventualConsistencyDB(num_replicas=3)

print("\n  --- Write Latency Comparison (100 writes) ---")

strong_latencies = [strong_db.write(f"key{i}", f"val{i}") for i in range(100)]
eventual_latencies = [eventual_db.write(f"key{i}", f"val{i}") for i in range(100)]

avg_strong = sum(strong_latencies) / len(strong_latencies)
avg_eventual = sum(eventual_latencies) / len(eventual_latencies)

print(f"    Strong Consistency:   avg {avg_strong:.2f}ms per write")
print(f"    Eventual Consistency: avg {avg_eventual:.4f}ms per write")
print(f"    Eventual is {avg_strong/avg_eventual:.0f}x faster!")

# Show staleness window
print("\n  --- Staleness Window Demo ---")
eventual_db2 = EventualConsistencyDB(num_replicas=3)
eventual_db2.write("counter", 42)
print(f"    Just wrote counter=42 to replica 0")
print(f"    Read from replica 0: {eventual_db2.read('counter', 0)} (up to date)")
print(f"    Read from replica 1: {eventual_db2.read('counter', 1)} (might be stale!)")
time.sleep(0.05)  # Wait for async replication
print(f"    Read from replica 1 (after sync): {eventual_db2.read('counter', 1)} (now consistent)")

print()


# ================================================================
# 5. QUORUM-BASED CONSISTENCY — Tunable!
# ================================================================

print("=" * 60)
print("  5. QUORUM CONSENSUS — Tunable Consistency")
print("=" * 60)


class QuorumDB:
    """
    Quorum-based system with tunable consistency.
    N = total replicas, W = write quorum, R = read quorum
    If W + R > N → strong consistency (guaranteed overlap)
    """

    def __init__(self, n: int = 5, w: int = 3, r: int = 3):
        self.n = n
        self.w = w
        self.r = r
        self.replicas = [Replica(f"Node-{i}") for i in range(n)]

    def write(self, key: str, value) -> str:
        ts = time.time()
        acks = 0
        for i, replica in enumerate(self.replicas):
            # Simulate some replicas being slow/unreachable
            if random.random() < 0.9:  # 90% success rate
                replica.local_write(key, value, ts)
                acks += 1

            if acks >= self.w:
                return f"Write OK (acked by {acks}/{self.n} nodes, needed {self.w})"

        return f"Write FAILED (only {acks}/{self.w} acks)"

    def read(self, key: str) -> str:
        responses = []
        for replica in self.replicas:
            entry = replica.data.get(key)
            if entry:
                responses.append(entry)
            if len(responses) >= self.r:
                break

        if len(responses) < self.r:
            return f"Read FAILED (only {len(responses)}/{self.r} responses)"

        # Return the value with the latest timestamp
        latest = max(responses, key=lambda x: x["timestamp"])
        return f"value = {latest['value']} (read from {len(responses)}/{self.n} nodes)"

    @property
    def is_strongly_consistent(self) -> bool:
        return self.w + self.r > self.n


# Different quorum configurations
configs = [
    (5, 3, 3, "Strong (W+R=6 > N=5)"),
    (5, 1, 1, "Weak (W+R=2 < N=5)"),
    (5, 5, 1, "Write-heavy strong (ALL writes)"),
    (5, 1, 5, "Read-heavy strong (ALL reads)"),
    (3, 2, 2, "Standard quorum"),
]

print(f"\n  {'Config':<30} {'N':>3} {'W':>3} {'R':>3} {'W+R':>5} {'Strong?':>8}")
print(f"  {'─'*30} {'─'*3} {'─'*3} {'─'*3} {'─'*5} {'─'*8}")

for n, w, r, label in configs:
    qdb = QuorumDB(n, w, r)
    strong = "YES" if qdb.is_strongly_consistent else "NO"
    print(f"  {label:<30} {n:>3} {w:>3} {r:>3} {w+r:>5} {strong:>8}")

print(f"""
  QUORUM RULES:
    W + R > N  →  Strong consistency (read/write overlap guaranteed)
    W + R <= N →  Eventual consistency (reads might miss latest write)
    W = 1      →  Fastest writes, weakest consistency
    R = 1      →  Fastest reads, weakest consistency
    W = N      →  Slowest writes, strongest write durability
    R = N      →  Slowest reads, strongest read consistency""")

print()


# ================================================================
# 6. CONFLICT RESOLUTION STRATEGIES
# ================================================================

print("=" * 60)
print("  6. CONFLICT RESOLUTION — What happens after partition?")
print("=" * 60)


# Last-Write-Wins (LWW)
print("\n  --- Strategy 1: Last-Write-Wins (LWW) ---")
print("    Simplest approach. Higher timestamp wins. May lose data!")

conflicts = [
    {"node": "NYC", "value": "Alice updated bio: 'Engineer'", "time": 1000.1},
    {"node": "LON", "value": "Alice updated bio: 'Senior Engineer'", "time": 1000.3},
]

winner = max(conflicts, key=lambda x: x["time"])
loser = min(conflicts, key=lambda x: x["time"])
print(f"    NYC wrote at t={conflicts[0]['time']}: {conflicts[0]['value']}")
print(f"    LON wrote at t={conflicts[1]['time']}: {conflicts[1]['value']}")
print(f"    Winner (LWW): {winner['node']} — {winner['value']}")
print(f"    Lost data: {loser['value']}")


# Merge strategy (for counters)
print("\n  --- Strategy 2: Merge (for counters/sets) ---")
print("    Instead of picking a winner, COMBINE the changes!")

nyc_counter = {"likes": 5}   # NYC saw 5 new likes during partition
lon_counter = {"likes": 3}   # London saw 3 new likes during partition
base_value = 42              # Value before partition

merged = base_value + nyc_counter["likes"] + lon_counter["likes"]
print(f"    Before partition: likes = {base_value}")
print(f"    NYC added: +{nyc_counter['likes']}")
print(f"    LON added: +{lon_counter['likes']}")
print(f"    Merged result: likes = {merged} (no data lost!)")


# Application-level resolution
print("\n  --- Strategy 3: Application-level (ask the user) ---")
print("    When automatic resolution is risky, let the user decide.")
print("    Example: Google Docs shows both versions and lets you pick.")
print("    Example: Git merge conflicts — developer resolves manually.")


print("\n" + "=" * 60)
print("  System Design Topic 3 Complete!")
print("  Say 'next' for Topic 4: Latency, Throughput & Estimation")
print("=" * 60)
