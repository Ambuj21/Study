"""
System Design Topic 9 - Database Replication: Python Simulations

Demonstrates:
- Primary-Replica replication with WAL (Write-Ahead Log)
- Sync vs Async replication performance comparison
- Replication lag measurement and its effects
- Automatic failover simulation
- Read scaling with multiple replicas

Usage:
    python code.py
"""
import time
import random
import threading
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict


# ================================================================
# 1. PRIMARY-REPLICA REPLICATION SIMULATION
# ================================================================

print("=" * 60)
print("  1. PRIMARY-REPLICA REPLICATION — WAL-based")
print("=" * 60)


@dataclass
class WALEntry:
    """Write-Ahead Log entry."""
    sequence: int
    operation: str  # INSERT, UPDATE, DELETE
    table: str
    data: dict
    timestamp: float = field(default_factory=time.time)


class DatabaseNode:
    """Simulates a database node (primary or replica)."""

    def __init__(self, name: str, is_primary: bool = False):
        self.name = name
        self.is_primary = is_primary
        self.data = {}
        self.wal = []  # Write-Ahead Log
        self.applied_sequence = 0
        self.reads = 0
        self.writes = 0
        self.lock = threading.Lock()

    def write(self, table: str, key: str, value: dict) -> WALEntry | None:
        if not self.is_primary:
            return None  # Replicas reject writes!

        with self.lock:
            self.writes += 1
            seq = len(self.wal) + 1
            entry = WALEntry(seq, "INSERT", table, {key: value})
            self.wal.append(entry)
            self.data[f"{table}:{key}"] = value
            return entry

    def apply_wal(self, entry: WALEntry):
        """Apply a WAL entry from primary (for replicas)."""
        with self.lock:
            for key, value in entry.data.items():
                self.data[f"{entry.table}:{key}"] = value
            self.applied_sequence = entry.sequence

    def read(self, table: str, key: str):
        self.reads += 1
        return self.data.get(f"{table}:{key}")

    @property
    def lag(self) -> int:
        """How many WAL entries behind the primary."""
        return len(self.wal) - self.applied_sequence if self.is_primary else 0


class ReplicationCluster:
    """Manages primary-replica replication."""

    def __init__(self, num_replicas: int = 3, mode: str = "async"):
        self.primary = DatabaseNode("Primary", is_primary=True)
        self.replicas = [DatabaseNode(f"Replica-{i+1}") for i in range(num_replicas)]
        self.mode = mode  # "sync", "async", "semi-sync"

    def write(self, table: str, key: str, value: dict) -> tuple[bool, float]:
        """Write to primary and replicate."""
        start = time.perf_counter()

        entry = self.primary.write(table, key, value)
        if not entry:
            return False, 0

        if self.mode == "sync":
            # Wait for ALL replicas
            for replica in self.replicas:
                time.sleep(0.002)  # Simulate network latency
                replica.apply_wal(entry)

        elif self.mode == "semi-sync":
            # Wait for at least ONE replica
            time.sleep(0.002)
            self.replicas[0].apply_wal(entry)
            # Others async
            for replica in self.replicas[1:]:
                threading.Thread(target=self._async_replicate,
                                args=(replica, entry), daemon=True).start()

        else:  # async
            # Don't wait — replicate in background
            for replica in self.replicas:
                threading.Thread(target=self._async_replicate,
                                args=(replica, entry), daemon=True).start()

        latency = (time.perf_counter() - start) * 1000
        return True, latency

    def _async_replicate(self, replica: DatabaseNode, entry: WALEntry):
        time.sleep(random.uniform(0.001, 0.01))  # Simulated network delay
        replica.apply_wal(entry)

    def read(self, table: str, key: str, from_primary: bool = False):
        if from_primary:
            return self.primary.read(table, key)
        # Round-robin across replicas
        replica = random.choice(self.replicas)
        return replica.read(table, key)


# Demo replication
cluster = ReplicationCluster(num_replicas=3, mode="async")

print(f"\n  --- Writing to Primary ---")
cluster.write("users", "1", {"name": "Alice", "age": 28})
cluster.write("users", "2", {"name": "Bob", "age": 32})
cluster.write("users", "3", {"name": "Charlie", "age": 25})

time.sleep(0.05)  # Wait for async replication

print(f"    Primary data:   {dict(list(cluster.primary.data.items())[:3])}")
for r in cluster.replicas:
    print(f"    {r.name} data: {dict(list(r.data.items())[:3])}")
    print(f"      Applied sequence: {r.applied_sequence} / {len(cluster.primary.wal)}")

print(f"\n    All replicas in sync!")

print()


# ================================================================
# 2. SYNC vs ASYNC vs SEMI-SYNC — Performance
# ================================================================

print("=" * 60)
print("  2. SYNC vs ASYNC vs SEMI-SYNC — Performance")
print("=" * 60)

NUM_WRITES = 200

for mode in ["async", "semi-sync", "sync"]:
    cluster = ReplicationCluster(num_replicas=3, mode=mode)
    latencies = []

    start = time.perf_counter()
    for i in range(NUM_WRITES):
        _, lat = cluster.write("users", str(i), {"name": f"User_{i}"})
        latencies.append(lat)
    total = (time.perf_counter() - start) * 1000

    avg_lat = sum(latencies) / len(latencies)
    p99 = sorted(latencies)[int(len(latencies) * 0.99)]

    print(f"\n  {mode.upper():>12}: {NUM_WRITES} writes in {total:.0f}ms")
    print(f"    Avg latency: {avg_lat:.2f}ms | P99: {p99:.2f}ms")
    print(f"    Writes/sec:  {NUM_WRITES / (total/1000):,.0f}")

    # Check data safety
    time.sleep(0.1)
    all_synced = all(r.applied_sequence == len(cluster.primary.wal)
                     for r in cluster.replicas)
    print(f"    Data safe on all replicas: {'YES' if all_synced else 'SYNCING...'}")

print(f"""
  SUMMARY:
    Async:     FASTEST writes, risk of data loss if primary crashes
    Semi-sync: Good balance — 1 replica confirmed before responding
    Sync:      SLOWEST writes, but zero data loss guaranteed""")

print()


# ================================================================
# 3. REPLICATION LAG — The Problem & Solutions
# ================================================================

print("=" * 60)
print("  3. REPLICATION LAG — Read-Your-Own-Writes Problem")
print("=" * 60)


class LagDemoCluster:
    """Demonstrates replication lag issues."""

    def __init__(self, lag_ms: float = 200):
        self.primary = {"profile:alice": {"name": "Alice", "photo": "old.jpg"}}
        self.replica = {"profile:alice": {"name": "Alice", "photo": "old.jpg"}}
        self.lag_ms = lag_ms
        self.last_write_time = {}

    def write(self, key: str, value: dict):
        self.primary[key] = value
        self.last_write_time[key] = time.time()
        # Replica will get this after lag_ms

    def read_from_replica(self, key: str):
        return self.replica.get(key)

    def read_from_primary(self, key: str):
        return self.primary.get(key)

    def read_your_writes(self, key: str, current_user: str):
        """Smart routing: read from primary if user just wrote."""
        last_write = self.last_write_time.get(key, 0)
        if time.time() - last_write < 10:  # Within 10 seconds of write
            return self.read_from_primary(key), "PRIMARY (fresh)"
        return self.read_from_replica(key), "REPLICA (fast)"

    def sync_replica(self):
        """Simulate replica catching up."""
        self.replica = dict(self.primary)


demo = LagDemoCluster(lag_ms=200)

print(f"\n  --- Problem: Read-Your-Own-Writes ---")
print(f"    Alice updates her profile photo...")
demo.write("profile:alice", {"name": "Alice", "photo": "NEW_selfie.jpg"})
print(f"    Primary:  {demo.read_from_primary('profile:alice')}")
print(f"    Replica:  {demo.read_from_replica('profile:alice')}")
print(f"    Alice reads from replica → sees OLD photo! BAD UX!")

print(f"\n  --- Solution: Smart Read Routing ---")
value, source = demo.read_your_writes("profile:alice", "alice")
print(f"    Alice reads → {value} (from {source})")
print(f"    Other users read from REPLICA (fast, slight lag is OK)")

print(f"\n  --- After replica syncs (200ms later) ---")
demo.sync_replica()
print(f"    Replica:  {demo.read_from_replica('profile:alice')} ✅ Now consistent!")

print()


# ================================================================
# 4. AUTOMATIC FAILOVER SIMULATION
# ================================================================

print("=" * 60)
print("  4. AUTOMATIC FAILOVER — Primary Dies!")
print("=" * 60)


class FailoverCluster:
    """Simulates automatic failover."""

    def __init__(self):
        self.primary = DatabaseNode("Primary", is_primary=True)
        self.replicas = [
            DatabaseNode("Replica-1"),
            DatabaseNode("Replica-2"),
        ]
        self.primary_alive = True
        self.failover_count = 0

    def write(self, key: str, value: dict) -> str:
        if not self.primary_alive:
            return "WRITE FAILED: Primary is down!"
        self.primary.write("data", key, value)
        # Async replicate (with simulated lag)
        for r in self.replicas:
            r.data[f"data:{key}"] = value
            r.applied_sequence += 1
        return f"Written to {self.primary.name}"

    def kill_primary(self):
        self.primary_alive = False
        print(f"    >>> {self.primary.name} CRASHED! <<<")

    def perform_failover(self):
        # Find best replica (most up-to-date)
        best = max(self.replicas, key=lambda r: r.applied_sequence)
        print(f"\n    FAILOVER PROCESS:")
        print(f"    1. Detected: {self.primary.name} is unreachable")

        for r in self.replicas:
            print(f"    2. {r.name}: applied_sequence = {r.applied_sequence}")

        print(f"    3. Promoting {best.name} (most up-to-date)")
        best.is_primary = True
        old_primary = self.primary
        self.primary = best
        self.primary_alive = True
        self.replicas = [r for r in self.replicas if r != best]
        self.failover_count += 1

        print(f"    4. {best.name} is now PRIMARY")
        print(f"    5. Remaining replicas: {[r.name for r in self.replicas]}")

        return best


fc = FailoverCluster()

print(f"\n  --- Normal operation ---")
for i in range(5):
    msg = fc.write(f"key_{i}", {"value": i})
    print(f"    {msg}: key_{i} = {i}")

print(f"\n  --- Primary crashes! ---")
fc.kill_primary()
msg = fc.write("key_5", {"value": 5})
print(f"    {msg}")

print(f"\n  --- Automatic failover ---")
new_primary = fc.perform_failover()

print(f"\n  --- After failover ---")
for i in range(5, 8):
    msg = fc.write(f"key_{i}", {"value": i})
    print(f"    {msg}: key_{i} = {i}")

print(f"\n  Total failovers: {fc.failover_count}")
print(f"  Data preserved: {len(fc.primary.data)} entries")

print()


# ================================================================
# 5. READ SCALING — Linear Scaling with Replicas
# ================================================================

print("=" * 60)
print("  5. READ SCALING — More Replicas = More Throughput")
print("=" * 60)


def simulate_read_throughput(num_replicas: int, requests: int = 2000,
                             server_qps: int = 500):
    """Simulate read throughput with N replicas."""
    total_capacity = num_replicas * server_qps

    start = time.perf_counter()
    served = 0
    dropped = 0

    # Simulate requests arriving
    per_replica = defaultdict(int)
    for i in range(requests):
        replica_idx = i % num_replicas
        per_replica[replica_idx] += 1
        if per_replica[replica_idx] <= server_qps:
            served += 1
        else:
            dropped += 1

    return served, dropped, total_capacity


REQUESTS = 5000

print(f"\n  {REQUESTS:,} read requests, each server handles 500 QPS max")
print(f"\n  {'Replicas':>10} {'Capacity':>10} {'Served':>8} {'Dropped':>9} {'Success':>9}")
print(f"  {'─'*10} {'─'*10} {'─'*8} {'─'*9} {'─'*9}")

for num_replicas in [1, 2, 3, 5, 10, 20]:
    served, dropped, capacity = simulate_read_throughput(num_replicas, REQUESTS)
    pct = served / REQUESTS * 100
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    print(f"  {num_replicas:>10} {capacity:>8} QPS {served:>8} {dropped:>9} {pct:>7.0f}%  {bar}")

print(f"""
  KEY INSIGHT: Read capacity scales LINEARLY!
    1 replica  =   500 QPS
    10 replicas = 5,000 QPS (10x!)

  This is why read-heavy apps (social media, news)
  add replicas rather than bigger servers.""")


# ================================================================
# 6. REPLICATION STATS — Real Numbers
# ================================================================

print()
print("=" * 60)
print("  6. REPLICATION IN PRODUCTION — Real Numbers")
print("=" * 60)

print(f"""
  ┌──────────────────────────────────────────────────────────┐
  │  Company         Replication Setup                       │
  ├──────────────────────────────────────────────────────────┤
  │  GitHub          1 primary + 5 replicas (PostgreSQL)     │
  │  Instagram       1 primary + 12 replicas per shard       │
  │  Shopify         1 primary + 5 replicas (MySQL)          │
  │  Stack Overflow  1 primary + 1 replica (SQL Server)      │
  │  Netflix         Multi-master (Cassandra, 3+ replicas)   │
  │  Google Spanner  5 replicas across 3 regions (sync!)     │
  └──────────────────────────────────────────────────────────┘

  TYPICAL PRODUCTION SETUP:
    Primary:    1 server (handles all writes)
    Replicas:   3-5 servers (handle reads)
    Replication: Semi-synchronous (1 sync + rest async)
    Failover:   Automatic (< 30 seconds)
    Lag target: < 100ms
""")


print("=" * 60)
print("  System Design Topic 9 Complete!")
print("  Say 'next' for Topic 10: Database Sharding")
print("=" * 60)
