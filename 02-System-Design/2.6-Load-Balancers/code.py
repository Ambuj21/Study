"""
System Design Topic 6 - Load Balancers: Python Simulations

Demonstrates:
- Load balancing algorithms (Round Robin, Weighted, Least Connections, IP Hash)
- Health check simulation
- Performance comparison of algorithms under different workloads
- Active-Passive failover simulation

Usage:
    python code.py
"""
import time
import random
import hashlib
import threading
from dataclasses import dataclass, field
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed


# ================================================================
# 1. LOAD BALANCING ALGORITHMS — All Implementations
# ================================================================

print("=" * 60)
print("  1. LOAD BALANCING ALGORITHMS — Side by Side")
print("=" * 60)


@dataclass
class Server:
    name: str
    weight: int = 1
    healthy: bool = True
    active_connections: int = 0
    total_handled: int = 0
    total_response_time: float = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    @property
    def avg_response_time(self) -> float:
        return self.total_response_time / self.total_handled if self.total_handled else 0

    def handle(self, processing_time: float = None):
        """Simulate handling a request."""
        with self._lock:
            self.active_connections += 1

        if processing_time is None:
            processing_time = random.uniform(5, 50) / 1000  # 5-50ms
        time.sleep(processing_time)

        with self._lock:
            self.active_connections -= 1
            self.total_handled += 1
            self.total_response_time += processing_time * 1000


# --- Round Robin ---
class RoundRobinLB:
    def __init__(self, servers: list[Server]):
        self.servers = servers
        self.index = 0

    def next_server(self) -> Server:
        healthy = [s for s in self.servers if s.healthy]
        if not healthy:
            return None
        server = healthy[self.index % len(healthy)]
        self.index += 1
        return server


# --- Weighted Round Robin ---
class WeightedRoundRobinLB:
    def __init__(self, servers: list[Server]):
        self.servers = servers
        self.pool = []
        for s in servers:
            self.pool.extend([s] * s.weight)
        self.index = 0

    def next_server(self) -> Server:
        healthy_pool = [s for s in self.pool if s.healthy]
        if not healthy_pool:
            return None
        server = healthy_pool[self.index % len(healthy_pool)]
        self.index += 1
        return server


# --- Least Connections ---
class LeastConnectionsLB:
    def __init__(self, servers: list[Server]):
        self.servers = servers

    def next_server(self) -> Server:
        healthy = [s for s in self.servers if s.healthy]
        if not healthy:
            return None
        return min(healthy, key=lambda s: s.active_connections)


# --- IP Hash ---
class IPHashLB:
    def __init__(self, servers: list[Server]):
        self.servers = servers

    def next_server(self, client_ip: str = None) -> Server:
        healthy = [s for s in self.servers if s.healthy]
        if not healthy:
            return None
        if client_ip is None:
            client_ip = f"192.168.1.{random.randint(1, 255)}"
        hash_val = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return healthy[hash_val % len(healthy)]


# --- Least Response Time ---
class LeastResponseTimeLB:
    def __init__(self, servers: list[Server]):
        self.servers = servers

    def next_server(self) -> Server:
        healthy = [s for s in self.servers if s.healthy]
        if not healthy:
            return None
        return min(healthy, key=lambda s: s.avg_response_time if s.total_handled > 0 else 0)


# Demo: Show distribution for each algorithm
def demo_distribution(name: str, lb, num_requests: int = 1000):
    """Show how requests are distributed."""
    distribution = defaultdict(int)

    for i in range(num_requests):
        if hasattr(lb, 'next_server') and 'client_ip' in lb.next_server.__code__.co_varnames:
            server = lb.next_server(f"10.0.{i//256}.{i%256}")
        else:
            server = lb.next_server()
        if server:
            distribution[server.name] += 1

    print(f"\n  {name} ({num_requests} requests):")
    for server_name in sorted(distribution.keys()):
        count = distribution[server_name]
        pct = count / num_requests * 100
        bar = "█" * int(pct / 2)
        print(f"    {server_name:<12} {count:>5} ({pct:>5.1f}%) {bar}")


# Create servers with different weights
servers_equal = [Server(f"S{i+1}", weight=1) for i in range(3)]
servers_weighted = [
    Server("S1-Power", weight=5),
    Server("S2-Medium", weight=3),
    Server("S3-Small", weight=1),
]

demo_distribution("Round Robin", RoundRobinLB([Server(f"S{i+1}") for i in range(3)]))
demo_distribution("Weighted RR", WeightedRoundRobinLB([
    Server("S1-Power", weight=5),
    Server("S2-Medium", weight=3),
    Server("S3-Small", weight=1),
]))
demo_distribution("IP Hash", IPHashLB([Server(f"S{i+1}") for i in range(3)]))

print()


# ================================================================
# 2. ALGORITHM PERFORMANCE UNDER LOAD
# ================================================================

print("=" * 60)
print("  2. PERFORMANCE COMPARISON — Under Real Load")
print("=" * 60)


def run_load_test(name: str, lb_class, servers: list[Server], num_requests: int = 300):
    """Run concurrent requests through a load balancer."""
    lb = lb_class(servers)
    latencies = []
    start_time = time.perf_counter()

    def make_request(i):
        if hasattr(lb.next_server, '__code__') and 'client_ip' in lb.next_server.__code__.co_varnames:
            server = lb.next_server(f"10.0.{i//256}.{i%256}")
        else:
            server = lb.next_server()
        if server:
            req_start = time.perf_counter()
            # Simulate different server speeds
            base_time = 10 if "Power" in server.name else 30 if "Medium" in server.name else 50
            server.handle(random.uniform(base_time, base_time + 20) / 1000)
            return (time.perf_counter() - req_start) * 1000
        return 0

    with ThreadPoolExecutor(max_workers=50) as pool:
        futures = [pool.submit(make_request, i) for i in range(num_requests)]
        for f in as_completed(futures):
            lat = f.result()
            if lat > 0:
                latencies.append(lat)

    elapsed = time.perf_counter() - start_time
    avg_lat = sum(latencies) / len(latencies) if latencies else 0
    p99 = sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0
    qps = len(latencies) / elapsed

    # Distribution
    dist = defaultdict(int)
    for s in servers:
        dist[s.name] = s.total_handled

    print(f"\n  {name}:")
    print(f"    QPS: {qps:,.0f} | Avg: {avg_lat:.1f}ms | P99: {p99:.1f}ms")
    for sname in sorted(dist.keys()):
        print(f"      {sname}: {dist[sname]} requests")


# Test with heterogeneous servers (different speeds)
print(f"\n  Servers: S1-Power (fast), S2-Medium, S3-Small (slow)")

algorithms = [
    ("Round Robin", RoundRobinLB),
    ("Weighted RR", WeightedRoundRobinLB),
    ("Least Connections", LeastConnectionsLB),
]

for algo_name, algo_class in algorithms:
    servers = [
        Server("S1-Power", weight=5),
        Server("S2-Medium", weight=3),
        Server("S3-Small", weight=1),
    ]
    run_load_test(algo_name, algo_class, servers, num_requests=300)

print()


# ================================================================
# 3. HEALTH CHECKS — Automatic Failure Detection
# ================================================================

print("=" * 60)
print("  3. HEALTH CHECKS — Dead Server Detection")
print("=" * 60)


class HealthCheckedLB:
    """Load balancer with health checking."""

    def __init__(self, servers: list[Server], check_interval: float = 0.1):
        self.servers = servers
        self.check_interval = check_interval
        self.healthy_threshold = 2
        self.unhealthy_threshold = 2
        self.check_counts = {s.name: 0 for s in servers}
        self.fail_counts = {s.name: 0 for s in servers}

    def health_check(self, server: Server) -> bool:
        """Simulate health check — returns True if healthy."""
        if not server.healthy:
            return False
        # Simulate occasional check failure
        return random.random() > 0.05  # 5% random failure rate

    def run_checks(self, rounds: int = 10):
        """Run health checks and show results."""
        for round_num in range(1, rounds + 1):
            results = []
            for server in self.servers:
                is_healthy = self.health_check(server)

                if is_healthy:
                    self.check_counts[server.name] += 1
                    self.fail_counts[server.name] = 0
                else:
                    self.fail_counts[server.name] += 1
                    self.check_counts[server.name] = 0

                status = "HEALTHY" if is_healthy else "FAILED"
                in_rotation = self.fail_counts[server.name] < self.unhealthy_threshold

                results.append((server.name, status, in_rotation))

            # Print round results
            status_str = " | ".join(
                f"{name}: {'✅' if ok else '❌'} {'(in rotation)' if rot else '(REMOVED!)'}"
                for name, ok, rot in results
            )
            print(f"    Round {round_num:>2}: {status_str}")


print(f"\n  --- All servers healthy ---")
servers = [Server("S1", healthy=True), Server("S2", healthy=True), Server("S3", healthy=True)]
lb_health = HealthCheckedLB(servers)
lb_health.run_checks(rounds=5)

print(f"\n  --- S2 crashes at round 3! ---")
servers = [Server("S1", healthy=True), Server("S2", healthy=True), Server("S3", healthy=True)]
lb_health = HealthCheckedLB(servers)

for round_num in range(1, 8):
    if round_num == 3:
        servers[1].healthy = False
        print(f"    >>> S2 CRASHES! <<<")
    if round_num == 6:
        servers[1].healthy = True
        print(f"    >>> S2 RECOVERS! <<<")

    results = []
    for server in servers:
        is_healthy = lb_health.health_check(server)
        if is_healthy:
            lb_health.fail_counts[server.name] = 0
        else:
            lb_health.fail_counts[server.name] += 1

        in_rotation = lb_health.fail_counts[server.name] < lb_health.unhealthy_threshold
        results.append((server.name, is_healthy, in_rotation))

    status_str = " | ".join(
        f"{name}: {'✅' if ok else '❌'}{'' if rot else ' REMOVED'}"
        for name, ok, rot in results
    )
    print(f"    Round {round_num}: {status_str}")

print()


# ================================================================
# 4. IP HASH — Session Affinity Demo
# ================================================================

print("=" * 60)
print("  4. IP HASH — Same Client Always Hits Same Server")
print("=" * 60)

servers = [Server(f"Server-{i+1}") for i in range(5)]
ip_lb = IPHashLB(servers)

print(f"\n  5 servers, mapping client IPs to servers:")
test_ips = ["192.168.1.1", "10.0.0.42", "172.16.0.100", "8.8.8.8", "1.1.1.1"]

for ip in test_ips:
    results = set()
    for _ in range(10):  # Same IP, 10 requests
        server = ip_lb.next_server(ip)
        results.add(server.name)

    consistency = "ALWAYS same server" if len(results) == 1 else f"INCONSISTENT ({len(results)} servers!)"
    print(f"    {ip:<20} → {list(results)[0] if len(results)==1 else results}  ({consistency})")

print(f"\n  KEY: Same IP ALWAYS maps to the same server!")
print(f"  Use case: Session affinity without cookies (stateful apps)")

print()


# ================================================================
# 5. ACTIVE-PASSIVE FAILOVER
# ================================================================

print("=" * 60)
print("  5. ACTIVE-PASSIVE FAILOVER SIMULATION")
print("=" * 60)


@dataclass
class LoadBalancerNode:
    name: str
    is_active: bool = False
    is_alive: bool = True
    requests_handled: int = 0


class ActivePassiveCluster:
    def __init__(self):
        self.active = LoadBalancerNode("LB-Primary", is_active=True)
        self.passive = LoadBalancerNode("LB-Standby", is_active=False)
        self.failover_count = 0

    def handle_request(self) -> str:
        if self.active.is_alive:
            self.active.requests_handled += 1
            return f"{self.active.name} handled request #{self.active.requests_handled}"
        else:
            # Failover!
            if not self.passive.is_active:
                self.failover_count += 1
                self.passive.is_active = True
                print(f"    !!! FAILOVER #{self.failover_count}: "
                      f"{self.active.name} is DOWN → {self.passive.name} takes over!")
            self.passive.requests_handled += 1
            return f"{self.passive.name} handled request #{self.passive.requests_handled}"

    def kill_active(self):
        self.active.is_alive = False

    def recover_active(self):
        self.active.is_alive = True
        self.passive.is_active = False
        print(f"    >>> {self.active.name} recovered! Back to primary.")


cluster = ActivePassiveCluster()

print(f"\n  --- Normal operation ---")
for i in range(3):
    print(f"    {cluster.handle_request()}")

print(f"\n  --- Primary LB crashes! ---")
cluster.kill_active()
for i in range(3):
    print(f"    {cluster.handle_request()}")

print(f"\n  --- Primary recovers ---")
cluster.recover_active()
for i in range(3):
    print(f"    {cluster.handle_request()}")

print(f"\n  Summary:")
print(f"    Primary handled:  {cluster.active.requests_handled} requests")
print(f"    Standby handled:  {cluster.passive.requests_handled} requests")
print(f"    Failovers:        {cluster.failover_count}")
print(f"    Zero requests lost!")


print("\n" + "=" * 60)
print("  System Design Topic 6 Complete!")
print("  Say 'next' for Topic 7: Caching — The Speed Layer")
print("=" * 60)
