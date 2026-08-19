"""
System Design Topic 1 - What Is System Design: Python Simulations

Demonstrates:
- Single server vs distributed architecture simulation
- Latency numbers visualization
- Back-of-envelope estimation calculator
- Availability calculator
- QPS (Queries Per Second) simulation

Usage:
    python code.py
"""
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor
import math


# ================================================================
# 1. LATENCY NUMBERS — Feel the difference
# ================================================================

print("=" * 60)
print("  1. LATENCY NUMBERS — Real measurements on YOUR machine")
print("=" * 60)


def measure_operations():
    """Measure actual latency of different operations."""

    # L1/L2 cache — simple arithmetic (stays in CPU cache)
    start = time.perf_counter_ns()
    x = 0
    for _ in range(1000):
        x += 1
    cpu_ns = (time.perf_counter_ns() - start) / 1000
    print(f"  CPU arithmetic (per op):     {cpu_ns:.1f} ns")

    # Dictionary lookup — in-memory hash table (simulates RAM cache)
    data = {f"key_{i}": f"value_{i}" for i in range(100_000)}
    start = time.perf_counter_ns()
    for _ in range(1000):
        _ = data["key_50000"]
    dict_ns = (time.perf_counter_ns() - start) / 1000
    print(f"  Dict lookup (RAM):           {dict_ns:.1f} ns")

    # List scan — simulates uncached access
    data_list = list(range(100_000))
    start = time.perf_counter_ns()
    for _ in range(100):
        _ = 99_999 in data_list
    list_ns = (time.perf_counter_ns() - start) / 100
    print(f"  List scan (100K items):       {list_ns:.0f} ns ({list_ns/1000:.1f} us)")

    # File I/O — disk access
    import tempfile
    import os
    temp_file = os.path.join(tempfile.gettempdir(), "sd_test.txt")
    with open(temp_file, "w") as f:
        f.write("x" * 10000)

    start = time.perf_counter_ns()
    for _ in range(100):
        with open(temp_file, "r") as f:
            _ = f.read()
    file_ns = (time.perf_counter_ns() - start) / 100
    print(f"  File read (10KB, SSD):        {file_ns:.0f} ns ({file_ns/1000:.0f} us)")
    os.remove(temp_file)

    # Network — DNS + TCP (simulated with socket)
    import socket
    start = time.perf_counter_ns()
    try:
        socket.getaddrinfo("google.com", 443)
        dns_ns = time.perf_counter_ns() - start
        print(f"  DNS lookup (google.com):      {dns_ns:.0f} ns ({dns_ns/1_000_000:.1f} ms)")
    except Exception:
        print(f"  DNS lookup: (network unavailable)")

    print(f"\n  KEY INSIGHT:")
    print(f"  Dict (RAM) is ~{file_ns/dict_ns:.0f}x faster than File (Disk)")
    print(f"  This is why we cache data in Redis (RAM) instead of querying DB (Disk)")


measure_operations()
print()


# ================================================================
# 2. SINGLE SERVER vs DISTRIBUTED — Load Simulation
# ================================================================

print("=" * 60)
print("  2. SINGLE SERVER vs MULTI-SERVER LOAD TEST")
print("=" * 60)


class SingleServer:
    """Simulates a single server handling requests."""

    def __init__(self, max_qps: int = 100):
        self.max_qps = max_qps
        self.current_load = 0
        self.failed = 0
        self.succeeded = 0
        self.lock = threading.Lock()

    def handle_request(self) -> bool:
        with self.lock:
            if self.current_load >= self.max_qps:
                self.failed += 1
                return False  # Server overloaded!
            self.current_load += 1

        time.sleep(random.uniform(0.001, 0.005))  # Simulate processing

        with self.lock:
            self.current_load -= 1
            self.succeeded += 1
        return True


class LoadBalancedCluster:
    """Simulates multiple servers behind a load balancer."""

    def __init__(self, num_servers: int = 3, max_qps_per_server: int = 100):
        self.servers = [SingleServer(max_qps_per_server) for _ in range(num_servers)]
        self.next_server = 0
        self.lock = threading.Lock()

    def handle_request(self) -> bool:
        # Round-robin load balancing
        with self.lock:
            server = self.servers[self.next_server]
            self.next_server = (self.next_server + 1) % len(self.servers)
        return server.handle_request()

    @property
    def total_succeeded(self):
        return sum(s.succeeded for s in self.servers)

    @property
    def total_failed(self):
        return sum(s.failed for s in self.servers)


def load_test(system, num_requests: int, label: str):
    """Send concurrent requests to a system."""
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=50) as pool:
        futures = [pool.submit(system.handle_request) for _ in range(num_requests)]
        for f in futures:
            f.result()

    elapsed = time.perf_counter() - start

    if hasattr(system, "total_succeeded"):
        succeeded = system.total_succeeded
        failed = system.total_failed
    else:
        succeeded = system.succeeded
        failed = system.failed

    qps = succeeded / elapsed if elapsed > 0 else 0
    print(f"\n  {label}:")
    print(f"    Requests: {num_requests}")
    print(f"    Succeeded: {succeeded} | Failed: {failed}")
    print(f"    Time: {elapsed:.3f}s")
    print(f"    Throughput: {qps:.0f} req/sec")
    print(f"    Success rate: {succeeded/(succeeded+failed)*100:.1f}%")
    return succeeded, failed


num_requests = 500

# Single server (capacity: 100 concurrent)
single = SingleServer(max_qps=100)
load_test(single, num_requests, "Single Server (capacity=100)")

# 3 servers behind load balancer (capacity: 300 concurrent)
cluster = LoadBalancedCluster(num_servers=3, max_qps_per_server=100)
load_test(cluster, num_requests, "3-Server Cluster (capacity=300)")

print()


# ================================================================
# 3. BACK-OF-ENVELOPE ESTIMATION CALCULATOR
# ================================================================

print("=" * 60)
print("  3. BACK-OF-ENVELOPE ESTIMATION")
print("=" * 60)


def estimate_system(
    name: str,
    total_users: int,
    dau_ratio: float,          # Daily Active Users as % of total
    actions_per_user_per_day: int,
    avg_data_size_bytes: int,
    read_write_ratio: int,     # e.g., 10 means 10 reads per 1 write
    has_media: bool = False,
    media_ratio: float = 0.0,
    avg_media_size_mb: float = 0.0,
    retention_years: int = 5,
):
    """Calculate storage, QPS, and bandwidth for a system."""

    dau = int(total_users * dau_ratio)
    daily_actions = dau * actions_per_user_per_day
    seconds_per_day = 86_400

    # QPS
    avg_qps = daily_actions / seconds_per_day
    peak_qps = avg_qps * 3  # Peak is typically 2-3x average
    write_qps = avg_qps / (1 + read_write_ratio)
    read_qps = avg_qps - write_qps

    # Storage
    daily_text_storage = daily_actions * avg_data_size_bytes
    daily_media_storage = daily_actions * media_ratio * avg_media_size_mb * 1_000_000 if has_media else 0
    daily_total_storage = daily_text_storage + daily_media_storage

    yearly_storage = daily_total_storage * 365
    total_storage = yearly_storage * retention_years

    # Bandwidth
    daily_bandwidth_out = daily_total_storage * read_write_ratio  # Outgoing (reads)

    def format_bytes(b):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if abs(b) < 1000:
                return f"{b:.1f} {unit}"
            b /= 1000
        return f"{b:.1f} EB"

    print(f"\n  === {name.upper()} ===")
    print(f"  Total Users:    {total_users:>15,}")
    print(f"  DAU:            {dau:>15,}")
    print(f"  Actions/day:    {daily_actions:>15,}")
    print(f"")
    print(f"  --- QPS ---")
    print(f"  Average QPS:    {avg_qps:>15,.0f}")
    print(f"  Peak QPS:       {peak_qps:>15,.0f}")
    print(f"  Read QPS:       {read_qps:>15,.0f}")
    print(f"  Write QPS:      {write_qps:>15,.0f}")
    print(f"")
    print(f"  --- Storage ---")
    print(f"  Daily:          {format_bytes(daily_total_storage):>15}")
    print(f"  Yearly:         {format_bytes(yearly_storage):>15}")
    print(f"  5-Year Total:   {format_bytes(total_storage):>15}")
    print(f"")
    print(f"  --- Bandwidth (outgoing) ---")
    print(f"  Daily:          {format_bytes(daily_bandwidth_out):>15}")
    print(f"  Per second:     {format_bytes(daily_bandwidth_out / 86400):>15}/s")


# Twitter-like system
estimate_system(
    name="Twitter-like App",
    total_users=500_000_000,
    dau_ratio=0.4,
    actions_per_user_per_day=2,
    avg_data_size_bytes=300,
    read_write_ratio=100,
    has_media=True,
    media_ratio=0.1,
    avg_media_size_mb=2,
    retention_years=5,
)

# Chat app
estimate_system(
    name="Chat App (WhatsApp-like)",
    total_users=2_000_000_000,
    dau_ratio=0.35,
    actions_per_user_per_day=50,
    avg_data_size_bytes=200,
    read_write_ratio=1,  # Roughly equal reads and writes
    has_media=True,
    media_ratio=0.05,
    avg_media_size_mb=3,
    retention_years=1,
)

print()


# ================================================================
# 4. AVAILABILITY CALCULATOR
# ================================================================

print("=" * 60)
print("  4. AVAILABILITY — How much downtime is acceptable?")
print("=" * 60)


def availability_report(percent: float, label: str):
    """Calculate downtime from availability percentage."""
    downtime_ratio = 1 - (percent / 100)
    yearly_minutes = 365.25 * 24 * 60
    monthly_minutes = 30 * 24 * 60

    yearly_down = downtime_ratio * yearly_minutes
    monthly_down = downtime_ratio * monthly_minutes

    # Format nicely
    if yearly_down >= 60 * 24:
        yearly_str = f"{yearly_down / (60*24):.1f} days"
    elif yearly_down >= 60:
        yearly_str = f"{yearly_down / 60:.1f} hours"
    else:
        yearly_str = f"{yearly_down:.1f} minutes"

    if monthly_down >= 60:
        monthly_str = f"{monthly_down / 60:.1f} hours"
    else:
        monthly_str = f"{monthly_down:.1f} minutes"

    nines = -math.log10(downtime_ratio) if downtime_ratio > 0 else float('inf')
    print(f"  {percent}% ({nines:.0f} nines) {label:25s} | Year: {yearly_str:>12s} | Month: {monthly_str:>10s}")


print()
availability_report(99.0, "Basic web app")
availability_report(99.9, "Standard SaaS")
availability_report(99.99, "High availability")
availability_report(99.999, "Mission critical")
availability_report(99.9999, "Ultra-high (financial)")


# Series vs Parallel availability
print(f"\n  --- Series vs Parallel ---")
a1, a2 = 0.999, 0.999

series = a1 * a2
parallel = 1 - (1 - a1) * (1 - a2)

print(f"  Two components at 99.9% each:")
print(f"    In SERIES  (both must work): {series*100:.4f}% = WORSE")
print(f"    In PARALLEL (either works):  {parallel*100:.6f}% = BETTER")
print(f"    LESSON: Add redundancy to increase availability!")

print()


# ================================================================
# 5. CACHE HIT SIMULATION — Why caching matters
# ================================================================

print("=" * 60)
print("  5. CACHE SIMULATION — 80/20 Rule in Action")
print("=" * 60)


def simulate_cache(num_requests: int, num_unique_items: int, cache_size: int):
    """Simulate cache hits/misses following Zipf distribution."""
    cache = {}  # Simple LRU-ish cache
    cache_order = []
    hits = 0
    misses = 0

    db_latency_ms = 10.0    # Database read: 10ms
    cache_latency_ms = 0.1  # Cache read: 0.1ms

    for _ in range(num_requests):
        # Zipf distribution: some items are accessed WAY more than others
        item_id = int(random.paretovariate(1.5)) % num_unique_items

        if item_id in cache:
            hits += 1
        else:
            misses += 1
            # Add to cache, evict oldest if full
            cache[item_id] = True
            cache_order.append(item_id)
            if len(cache) > cache_size:
                evicted = cache_order.pop(0)
                cache.pop(evicted, None)

    hit_rate = hits / num_requests * 100
    avg_latency = (hits * cache_latency_ms + misses * db_latency_ms) / num_requests
    no_cache_latency = db_latency_ms

    print(f"\n  Requests: {num_requests:,} | Unique items: {num_unique_items:,} | Cache size: {cache_size:,}")
    print(f"  Cache hits: {hits:,} ({hit_rate:.1f}%) | Misses: {misses:,}")
    print(f"  Avg latency WITH cache:    {avg_latency:.2f} ms")
    print(f"  Avg latency WITHOUT cache: {no_cache_latency:.2f} ms")
    print(f"  Cache makes it {no_cache_latency/avg_latency:.1f}x faster!")


# Small cache, big impact (80/20 rule)
simulate_cache(num_requests=10_000, num_unique_items=10_000, cache_size=100)
simulate_cache(num_requests=10_000, num_unique_items=10_000, cache_size=1_000)
simulate_cache(num_requests=10_000, num_unique_items=10_000, cache_size=5_000)


print("\n" + "=" * 60)
print("  System Design Topic 1 Complete!")
print("  Say 'next' for Topic 2: Scalability")
print("=" * 60)
