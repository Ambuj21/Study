"""
System Design Topic 2 - Scalability: Python Simulations

Demonstrates:
- Vertical vs horizontal scaling performance
- Stateful vs stateless server behavior
- Auto-scaling simulation
- Session management strategies (in-memory, Redis-like, JWT-like)
- Cost comparison calculator

Usage:
    python code.py
"""
import time
import random
import threading
import hashlib
import json
import base64
import hmac
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field


# ================================================================
# 1. VERTICAL vs HORIZONTAL SCALING SIMULATION
# ================================================================

print("=" * 60)
print("  1. VERTICAL vs HORIZONTAL SCALING")
print("=" * 60)


class Server:
    """Simulates a server with CPU capacity."""

    def __init__(self, name: str, cpu_cores: int, ram_gb: int):
        self.name = name
        self.cpu_cores = cpu_cores
        self.ram_gb = ram_gb
        self.max_concurrent = cpu_cores * 50  # ~50 requests per core
        self.active_requests = 0
        self.total_handled = 0
        self.total_rejected = 0
        self.lock = threading.Lock()

    def handle_request(self) -> tuple[bool, float]:
        """Returns (success, latency_ms)."""
        with self.lock:
            if self.active_requests >= self.max_concurrent:
                self.total_rejected += 1
                return False, 0
            self.active_requests += 1

        # Simulate processing (slower when more loaded)
        load_factor = self.active_requests / self.max_concurrent
        base_latency = 5  # 5ms base
        latency = base_latency * (1 + load_factor * 3)  # Degrades under load
        time.sleep(latency / 1000)

        with self.lock:
            self.active_requests -= 1
            self.total_handled += 1

        return True, latency


class LoadBalancer:
    """Round-robin load balancer across multiple servers."""

    def __init__(self, servers: list[Server]):
        self.servers = servers
        self.counter = 0
        self.lock = threading.Lock()

    def route_request(self) -> tuple[bool, float, str]:
        with self.lock:
            server = self.servers[self.counter % len(self.servers)]
            self.counter += 1

        success, latency = server.handle_request()
        return success, latency, server.name


def run_load_test(label: str, handler, num_requests: int, max_workers: int = 100):
    """Run a load test and return results."""
    latencies = []
    failures = 0
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(handler) for _ in range(num_requests)]
        for f in as_completed(futures):
            result = f.result()
            if isinstance(result, tuple):
                success, latency = result[0], result[1]
            else:
                success, latency = result, 0

            if success:
                latencies.append(latency)
            else:
                failures += 1

    elapsed = time.perf_counter() - start
    succeeded = len(latencies)
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    p99_latency = sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0
    qps = succeeded / elapsed

    print(f"\n  {label}:")
    print(f"    Requests:  {num_requests:,}")
    print(f"    Succeeded: {succeeded:,} | Failed: {failures:,}")
    print(f"    QPS:       {qps:,.0f} req/sec")
    print(f"    Avg Latency: {avg_latency:.1f}ms | P99: {p99_latency:.1f}ms")
    print(f"    Success Rate: {succeeded/(succeeded+failures)*100:.1f}%")

    return {"qps": qps, "avg_latency": avg_latency, "success_rate": succeeded/(succeeded+failures)*100}


NUM_REQUESTS = 1000

# Scenario A: One big server (vertical scaling)
big_server = Server("big-server", cpu_cores=16, ram_gb=64)
print("\n  --- Vertical Scaling: 1 big server (16 CPU, 64 GB) ---")
result_v = run_load_test(
    "Single Big Server",
    big_server.handle_request,
    NUM_REQUESTS
)

# Scenario B: Four small servers (horizontal scaling)
small_servers = [Server(f"server-{i+1}", cpu_cores=4, ram_gb=16) for i in range(4)]
lb = LoadBalancer(small_servers)
print("\n  --- Horizontal Scaling: 4 small servers (4 CPU, 16 GB each) ---")
result_h = run_load_test(
    "4-Server Cluster",
    lb.route_request,
    NUM_REQUESTS
)

# Comparison
print(f"\n  === COMPARISON ===")
print(f"    {'Metric':<20} {'Vertical':>15} {'Horizontal':>15}")
print(f"    {'─'*20} {'─'*15} {'─'*15}")
print(f"    {'QPS':<20} {result_v['qps']:>12,.0f}    {result_h['qps']:>12,.0f}")
print(f"    {'Avg Latency':<20} {result_v['avg_latency']:>11.1f}ms   {result_h['avg_latency']:>11.1f}ms")
print(f"    {'Success Rate':<20} {result_v['success_rate']:>11.1f}%   {result_h['success_rate']:>11.1f}%")
print(f"    {'Total CPU Cores':<20} {'16':>15} {'16 (4x4)':>15}")
print(f"    {'Fault Tolerant?':<20} {'NO':>15} {'YES':>15}")

print()


# ================================================================
# 2. STATEFUL vs STATELESS SERVER
# ================================================================

print("=" * 60)
print("  2. STATEFUL vs STATELESS SERVER DEMO")
print("=" * 60)


# --- Stateful Server (session in local memory) ---
class StatefulServer:
    def __init__(self, name: str):
        self.name = name
        self.sessions = {}  # Local storage — lost if server dies!

    def login(self, user: str) -> str:
        session_id = hashlib.md5(f"{user}{time.time()}".encode()).hexdigest()[:8]
        self.sessions[session_id] = {"user": user, "cart": []}
        return session_id

    def get_cart(self, session_id: str) -> list | None:
        session = self.sessions.get(session_id)
        return session["cart"] if session else None

    def add_to_cart(self, session_id: str, item: str) -> bool:
        session = self.sessions.get(session_id)
        if session:
            session["cart"].append(item)
            return True
        return False


print("\n  --- STATEFUL: Sessions in server memory ---")
server_a = StatefulServer("Server-A")
server_b = StatefulServer("Server-B")

# User logs in on Server A
session = server_a.login("Alice")
server_a.add_to_cart(session, "Laptop")
print(f"    Alice logs in on {server_a.name}, session: {session}")
print(f"    Cart on {server_a.name}: {server_a.get_cart(session)}")

# Next request goes to Server B (load balancer routes differently)
cart_on_b = server_b.get_cart(session)
print(f"    Cart on {server_b.name}: {cart_on_b}")
print(f"    PROBLEM: Session not found on Server B!")


# --- Stateless Server with shared session store ---
class SharedSessionStore:
    """Simulates Redis — shared session storage."""

    def __init__(self):
        self.data = {}

    def set(self, key: str, value: dict, ttl: int = 3600):
        self.data[key] = {"value": value, "expires": time.time() + ttl}

    def get(self, key: str) -> dict | None:
        entry = self.data.get(key)
        if entry and time.time() < entry["expires"]:
            return entry["value"]
        return None


class StatelessServer:
    def __init__(self, name: str, session_store: SharedSessionStore):
        self.name = name
        self.store = session_store  # External shared store

    def login(self, user: str) -> str:
        session_id = hashlib.md5(f"{user}{time.time()}".encode()).hexdigest()[:8]
        self.store.set(session_id, {"user": user, "cart": []})
        return session_id

    def get_cart(self, session_id: str) -> list | None:
        session = self.store.get(session_id)
        return session["cart"] if session else None

    def add_to_cart(self, session_id: str, item: str) -> bool:
        session = self.store.get(session_id)
        if session:
            session["cart"].append(item)
            self.store.set(session_id, session)
            return True
        return False


print("\n  --- STATELESS: Sessions in shared Redis ---")
redis = SharedSessionStore()
server_x = StatelessServer("Server-X", redis)
server_y = StatelessServer("Server-Y", redis)

# User logs in on Server X
session = server_x.login("Alice")
server_x.add_to_cart(session, "Laptop")
print(f"    Alice logs in on {server_x.name}, session: {session}")
print(f"    Cart on {server_x.name}: {server_x.get_cart(session)}")

# Next request goes to Server Y — works perfectly!
cart_on_y = server_y.get_cart(session)
print(f"    Cart on {server_y.name}: {cart_on_y}")
print(f"    SUCCESS: Session found on ANY server!")


# --- JWT approach ---
print("\n  --- JWT: Session IN the token (no server storage!) ---")

JWT_SECRET = "super_secret_key_123"


def jwt_encode(payload: dict) -> str:
    """Simple JWT-like encoding."""
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256"}).encode()).decode()
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    signature = hmac.new(JWT_SECRET.encode(), f"{header}.{body}".encode(), hashlib.sha256).hexdigest()[:16]
    return f"{header}.{body}.{signature}"


def jwt_decode(token: str) -> dict | None:
    """Simple JWT-like decoding."""
    try:
        header, body, signature = token.split(".")
        expected_sig = hmac.new(JWT_SECRET.encode(), f"{header}.{body}".encode(), hashlib.sha256).hexdigest()[:16]
        if signature != expected_sig:
            return None  # Tampered!
        return json.loads(base64.urlsafe_b64decode(body))
    except Exception:
        return None


token = jwt_encode({"user": "Alice", "role": "customer", "exp": int(time.time()) + 3600})
print(f"    JWT Token: {token[:50]}...")
print(f"    Decoded: {jwt_decode(token)}")
print(f"    No Redis needed! Token carries the session data.")
print(f"    ANY server can verify it with the secret key.")

# Tamper detection
tampered = token[:-1] + "X"
print(f"    Tampered token decoded: {jwt_decode(tampered)}")
print(f"    Tampered tokens are REJECTED!")

print()


# ================================================================
# 3. AUTO-SCALING SIMULATION
# ================================================================

print("=" * 60)
print("  3. AUTO-SCALING SIMULATION (24-hour traffic)")
print("=" * 60)


def get_traffic(hour: int) -> int:
    """Simulate realistic daily traffic pattern."""
    # Low at night, peaks at lunch and evening
    patterns = {
        0: 200, 1: 100, 2: 80, 3: 50, 4: 50, 5: 100,
        6: 300, 7: 600, 8: 1200, 9: 2000, 10: 2500, 11: 3000,
        12: 3500, 13: 3200, 14: 2800, 15: 2500, 16: 2800, 17: 3000,
        18: 3500, 19: 4000, 20: 4500, 21: 4000, 22: 2500, 23: 800,
    }
    return patterns.get(hour, 1000)


@dataclass
class AutoScaler:
    min_servers: int = 2
    max_servers: int = 20
    current_servers: int = 2
    capacity_per_server: int = 500  # requests/sec per server

    scale_up_threshold: float = 0.8    # Scale up at 80% capacity
    scale_down_threshold: float = 0.3  # Scale down at 30% capacity

    def evaluate(self, traffic: int) -> str:
        total_capacity = self.current_servers * self.capacity_per_server
        utilization = traffic / total_capacity

        action = "hold"

        if utilization > self.scale_up_threshold and self.current_servers < self.max_servers:
            needed = max(1, int((traffic / (self.capacity_per_server * 0.6)) - self.current_servers))
            added = min(needed, self.max_servers - self.current_servers)
            self.current_servers += added
            action = f"+{added} servers"

        elif utilization < self.scale_down_threshold and self.current_servers > self.min_servers:
            self.current_servers = max(self.min_servers, self.current_servers - 1)
            action = "-1 server"

        new_capacity = self.current_servers * self.capacity_per_server
        new_util = traffic / new_capacity * 100

        return (f"  {str(traffic):>6} req/s | "
                f"{self.current_servers:>2} servers | "
                f"Capacity: {new_capacity:>6} | "
                f"Util: {new_util:>5.1f}% | "
                f"Action: {action}")


scaler = AutoScaler()

print(f"\n  {'Hour':>6} | {'Traffic':>10} | {'Servers':>8} | {'Capacity':>9} | {'Util':>6} | Action")
print(f"  {'─'*6} | {'─'*10} | {'─'*8} | {'─'*9} | {'─'*6} | {'─'*12}")

for hour in range(24):
    traffic = get_traffic(hour)
    result = scaler.evaluate(traffic)
    print(f"  {hour:02d}:00 |{result}")

print()


# ================================================================
# 4. SCALING COST COMPARISON
# ================================================================

print("=" * 60)
print("  4. COST COMPARISON — Vertical vs Horizontal")
print("=" * 60)

cost_data = [
    # (name, cpu, ram_gb, monthly_cost, max_concurrent)
    ("Small (t3.small)", 2, 2, 15, 100),
    ("Medium (t3.xlarge)", 4, 16, 120, 500),
    ("Large (m5.4xlarge)", 16, 64, 560, 5000),
    ("XLarge (m5.16xlarge)", 64, 256, 2200, 20000),
    ("Mega (x1.32xlarge)", 128, 1952, 13300, 50000),
]

print(f"\n  {'Server Type':<25} {'CPU':>5} {'RAM':>8} {'Cost/mo':>10} {'Max Users':>10} {'$/User':>10}")
print(f"  {'─'*25} {'─'*5} {'─'*8} {'─'*10} {'─'*10} {'─'*10}")

for name, cpu, ram, cost, users in cost_data:
    cost_per_user = cost / users
    print(f"  {name:<25} {cpu:>5} {ram:>6}GB ${cost:>8,} {users:>10,} ${cost_per_user:>8.2f}")

# Horizontal comparison
target_users = 20000
small_cost = 120  # t3.xlarge
small_capacity = 500
servers_needed = (target_users + small_capacity - 1) // small_capacity
horizontal_cost = servers_needed * small_cost

vertical_cost = 2200  # m5.16xlarge

print(f"\n  --- For {target_users:,} users ---")
print(f"  Vertical: 1x m5.16xlarge     = ${vertical_cost:,}/month")
print(f"  Horizontal: {servers_needed}x t3.xlarge     = ${horizontal_cost:,}/month")
print(f"  Savings with horizontal: ${vertical_cost - horizontal_cost:,}/month ({(1 - horizontal_cost/vertical_cost)*100:.0f}% cheaper)")
print(f"  PLUS: Horizontal gives fault tolerance (vertical doesn't)!")

print()


# ================================================================
# 5. FAULT TOLERANCE DEMO
# ================================================================

print("=" * 60)
print("  5. FAULT TOLERANCE — Server crash simulation")
print("=" * 60)


def simulate_fault_tolerance(num_servers: int, crash_probability: float, num_requests: int):
    """Simulate requests with random server crashes."""
    servers_alive = [True] * num_servers
    handled = 0
    failed = 0

    for i in range(num_requests):
        # Randomly crash a server
        if random.random() < crash_probability:
            victim = random.randint(0, num_servers - 1)
            servers_alive[victim] = False

        # Try to route to an alive server
        alive_servers = [j for j, alive in enumerate(servers_alive) if alive]
        if alive_servers:
            handled += 1
        else:
            failed += 1

        # Recovery: restart crashed servers occasionally
        if i % 100 == 0:
            for j in range(num_servers):
                if not servers_alive[j] and random.random() < 0.5:
                    servers_alive[j] = True

    availability = handled / num_requests * 100
    return availability


print()
for n_servers in [1, 2, 3, 5, 10]:
    avail = simulate_fault_tolerance(n_servers, crash_probability=0.01, num_requests=10000)
    bar = "█" * int(avail / 5) + "░" * (20 - int(avail / 5))
    print(f"  {n_servers:>2} servers: {bar} {avail:.2f}%")

print(f"\n  LESSON: More servers = higher availability even with crashes!")


print("\n" + "=" * 60)
print("  System Design Topic 2 Complete!")
print("  Say 'next' for Topic 3: CAP Theorem & Trade-offs")
print("=" * 60)
