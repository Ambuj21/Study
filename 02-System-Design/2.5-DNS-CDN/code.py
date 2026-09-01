"""
System Design Topic 5 - DNS & CDN: Python Simulations

Demonstrates:
- DNS resolution with caching (TTL behavior)
- Real DNS lookups on your machine
- CDN simulation (cache hit/miss, edge servers)
- CDN impact calculator (bandwidth savings)
- Cache invalidation strategies

Usage:
    python code.py
"""
import time
import socket
import random
import hashlib
from dataclasses import dataclass, field
from collections import OrderedDict


# ================================================================
# 1. REAL DNS LOOKUPS ON YOUR MACHINE
# ================================================================

print("=" * 60)
print("  1. REAL DNS LOOKUPS — Measuring Latency")
print("=" * 60)

domains = [
    "google.com",
    "github.com",
    "amazon.com",
    "cloudflare.com",
    "netflix.com",
]

print(f"\n  {'Domain':<25} {'IP Address':<20} {'Time':>10}")
print(f"  {'─'*25} {'─'*20} {'─'*10}")

for domain in domains:
    start = time.perf_counter_ns()
    try:
        ip = socket.gethostbyname(domain)
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
        print(f"  {domain:<25} {ip:<20} {elapsed_ms:>8.2f}ms")
    except Exception as e:
        print(f"  {domain:<25} {'(failed)':<20} —")

# Cached lookup — should be much faster
print(f"\n  --- Second lookup (cached by OS) ---")
for domain in domains[:3]:
    start = time.perf_counter_ns()
    try:
        ip = socket.gethostbyname(domain)
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
        print(f"  {domain:<25} {ip:<20} {elapsed_ms:>8.2f}ms")
    except Exception:
        pass

print(f"\n  INSIGHT: Second lookup is faster because the OS cached the result!")

print()


# ================================================================
# 2. DNS RESOLVER SIMULATOR
# ================================================================

print("=" * 60)
print("  2. DNS RESOLVER — Simulating the Hierarchy")
print("=" * 60)


class DNSCache:
    """Simulates DNS cache with TTL."""

    def __init__(self, name: str):
        self.name = name
        self.cache = {}  # {domain: {"ip": ip, "expires": timestamp}}
        self.hits = 0
        self.misses = 0

    def lookup(self, domain: str) -> str | None:
        entry = self.cache.get(domain)
        if entry and time.time() < entry["expires"]:
            self.hits += 1
            return entry["ip"]
        self.misses += 1
        return None

    def store(self, domain: str, ip: str, ttl: int):
        self.cache[domain] = {"ip": ip, "expires": time.time() + ttl}


class DNSResolver:
    """Simulates recursive DNS resolution."""

    def __init__(self):
        self.browser_cache = DNSCache("Browser Cache")
        self.os_cache = DNSCache("OS Cache")
        self.isp_cache = DNSCache("ISP Resolver")

        # Authoritative records (the source of truth)
        self.authoritative = {
            "google.com":    {"ip": "142.250.190.78",  "ttl": 300},
            "github.com":    {"ip": "140.82.121.4",    "ttl": 60},
            "myapp.com":     {"ip": "52.14.88.201",    "ttl": 3600},
            "api.myapp.com": {"ip": "52.14.88.205",    "ttl": 120},
        }
        self.resolution_log = []

    def resolve(self, domain: str) -> tuple[str, list[str]]:
        """Resolve domain, return (IP, steps taken)."""
        steps = []

        # Step 1: Browser cache
        ip = self.browser_cache.lookup(domain)
        if ip:
            steps.append(f"Browser cache HIT: {ip}")
            return ip, steps
        steps.append("Browser cache MISS")

        # Step 2: OS cache
        ip = self.os_cache.lookup(domain)
        if ip:
            steps.append(f"OS cache HIT: {ip}")
            self.browser_cache.store(domain, ip, 60)
            return ip, steps
        steps.append("OS cache MISS")

        # Step 3: ISP Recursive resolver
        ip = self.isp_cache.lookup(domain)
        if ip:
            steps.append(f"ISP resolver HIT: {ip}")
            self.os_cache.store(domain, ip, 300)
            self.browser_cache.store(domain, ip, 60)
            return ip, steps
        steps.append("ISP resolver MISS")

        # Step 4: Full resolution (Root → TLD → Authoritative)
        steps.append("Querying Root server → '.com' TLD")
        steps.append(f"Querying .com TLD → '{domain}' nameserver")

        record = self.authoritative.get(domain)
        if record:
            ip = record["ip"]
            ttl = record["ttl"]
            steps.append(f"Authoritative answer: {ip} (TTL: {ttl}s)")
            self.isp_cache.store(domain, ip, ttl)
            self.os_cache.store(domain, ip, min(ttl, 300))
            self.browser_cache.store(domain, ip, min(ttl, 60))
            return ip, steps

        steps.append("NXDOMAIN — domain not found!")
        return "NOT FOUND", steps


resolver = DNSResolver()

# First resolution — full path
print(f"\n  --- First lookup: myapp.com ---")
ip, steps = resolver.resolve("myapp.com")
for i, step in enumerate(steps, 1):
    print(f"    Step {i}: {step}")
print(f"  Result: {ip}")

# Second resolution — cached!
print(f"\n  --- Second lookup: myapp.com (cached!) ---")
ip, steps = resolver.resolve("myapp.com")
for i, step in enumerate(steps, 1):
    print(f"    Step {i}: {step}")
print(f"  Result: {ip} (instant!)")

# Different domain
print(f"\n  --- New domain: github.com ---")
ip, steps = resolver.resolve("github.com")
for i, step in enumerate(steps, 1):
    print(f"    Step {i}: {step}")
print(f"  Result: {ip}")

# Stats
print(f"\n  Cache Statistics:")
for cache in [resolver.browser_cache, resolver.os_cache, resolver.isp_cache]:
    total = cache.hits + cache.misses
    hit_rate = cache.hits / total * 100 if total > 0 else 0
    print(f"    {cache.name:<20}: {cache.hits} hits, {cache.misses} misses ({hit_rate:.0f}% hit rate)")

print()


# ================================================================
# 3. CDN SIMULATION
# ================================================================

print("=" * 60)
print("  3. CDN SIMULATION — Edge Caching in Action")
print("=" * 60)


@dataclass
class EdgeServer:
    """Simulates a CDN edge server."""
    location: str
    cache: OrderedDict = field(default_factory=OrderedDict)
    max_cache_size: int = 100  # MB
    current_size: float = 0
    hits: int = 0
    misses: int = 0

    def get(self, url: str) -> tuple[bool, float]:
        """Get content. Returns (cache_hit, latency_ms)."""
        if url in self.cache:
            self.hits += 1
            return True, random.uniform(2, 10)  # Edge latency: 2-10ms

        self.misses += 1
        return False, 0

    def store(self, url: str, size_kb: float):
        """Cache content at this edge."""
        size_mb = size_kb / 1024
        # Evict old entries if full
        while self.current_size + size_mb > self.max_cache_size and self.cache:
            _, evicted_size = self.cache.popitem(last=False)
            self.current_size -= evicted_size

        self.cache[url] = size_mb
        self.current_size += size_mb

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total * 100 if total > 0 else 0


class CDNSimulator:
    """Simulates a CDN with multiple edge servers."""

    def __init__(self):
        self.edges = {
            "NYC":    EdgeServer("New York",    max_cache_size=500),
            "LON":    EdgeServer("London",      max_cache_size=500),
            "TOK":    EdgeServer("Tokyo",       max_cache_size=500),
            "SYD":    EdgeServer("Sydney",      max_cache_size=500),
        }
        self.origin_requests = 0
        self.origin_latency_ms = 150  # Origin server latency

    def request(self, url: str, user_location: str, size_kb: float) -> tuple[str, float]:
        """Handle a CDN request. Returns (source, latency_ms)."""
        edge = self.edges[user_location]

        # Check edge cache
        hit, latency = edge.get(url)
        if hit:
            return f"EDGE-{user_location}", latency

        # Cache miss — fetch from origin
        self.origin_requests += 1
        origin_latency = self.origin_latency_ms + random.uniform(0, 50)

        # Cache at edge for future requests
        edge.store(url, size_kb)

        return "ORIGIN", origin_latency


cdn = CDNSimulator()

# Simulate traffic patterns
print(f"\n  --- Simulating 1,000 requests across 4 regions ---")

# Content catalog: popular items are requested more (Zipf distribution)
content = [(f"/img/product_{i}.jpg", random.uniform(50, 500)) for i in range(200)]
locations = ["NYC", "LON", "TOK", "SYD"]

total_latency = 0
edge_count = 0
origin_count = 0

for _ in range(1000):
    # Zipf-like: popular items requested more often
    idx = min(int(random.paretovariate(1.5)), len(content) - 1)
    url, size = content[idx]
    location = random.choice(locations)

    source, latency = cdn.request(url, location, size)
    total_latency += latency

    if source.startswith("EDGE"):
        edge_count += 1
    else:
        origin_count += 1

avg_latency = total_latency / 1000

print(f"\n  Results:")
print(f"    Total requests:     1,000")
print(f"    Edge hits:          {edge_count:,} ({edge_count/10:.1f}%)")
print(f"    Origin fetches:     {origin_count:,} ({origin_count/10:.1f}%)")
print(f"    Avg latency:        {avg_latency:.1f}ms")
print(f"    Without CDN:        ~{cdn.origin_latency_ms + 25:.0f}ms avg")
print(f"    CDN speedup:        {(cdn.origin_latency_ms + 25)/avg_latency:.1f}x faster!")

print(f"\n  Per-region cache stats:")
print(f"    {'Region':<12} {'Hits':>6} {'Misses':>8} {'Hit Rate':>10} {'Cached':>10}")
print(f"    {'─'*12} {'─'*6} {'─'*8} {'─'*10} {'─'*10}")
for loc, edge in cdn.edges.items():
    print(f"    {edge.location:<12} {edge.hits:>6} {edge.misses:>8} {edge.hit_rate:>9.1f}% {edge.current_size:>8.0f}MB")

print()


# ================================================================
# 4. CDN BANDWIDTH SAVINGS CALCULATOR
# ================================================================

print("=" * 60)
print("  4. CDN IMPACT — Bandwidth & Cost Savings")
print("=" * 60)


def calculate_cdn_impact(
    daily_page_views: int,
    assets_per_page: int,
    avg_asset_size_kb: float,
    cdn_hit_rate: float,
    origin_bandwidth_cost_per_gb: float = 0.09,  # AWS pricing
    cdn_bandwidth_cost_per_gb: float = 0.02,     # CloudFlare-like
):
    """Calculate CDN savings."""

    daily_asset_requests = daily_page_views * assets_per_page
    daily_bandwidth_gb = (daily_asset_requests * avg_asset_size_kb) / (1024 * 1024)

    # Without CDN — origin handles everything
    origin_only_cost = daily_bandwidth_gb * origin_bandwidth_cost_per_gb

    # With CDN
    cdn_bandwidth = daily_bandwidth_gb * cdn_hit_rate
    origin_bandwidth = daily_bandwidth_gb * (1 - cdn_hit_rate)
    cdn_cost = cdn_bandwidth * cdn_bandwidth_cost_per_gb + origin_bandwidth * origin_bandwidth_cost_per_gb
    savings = origin_only_cost - cdn_cost

    print(f"\n  Daily page views:     {daily_page_views:>15,}")
    print(f"  Assets per page:      {assets_per_page:>15}")
    print(f"  Daily asset requests: {daily_asset_requests:>15,}")
    print(f"  Daily bandwidth:      {daily_bandwidth_gb:>12,.1f} GB")
    print(f"  CDN hit rate:         {cdn_hit_rate*100:>14.0f}%")
    print(f"")
    print(f"  WITHOUT CDN:")
    print(f"    Origin bandwidth:   {daily_bandwidth_gb:>12,.1f} GB/day")
    print(f"    Origin daily cost:  ${origin_only_cost:>11,.2f}")
    print(f"    Origin monthly:     ${origin_only_cost * 30:>11,.2f}")
    print(f"")
    print(f"  WITH CDN:")
    print(f"    CDN serves:         {cdn_bandwidth:>12,.1f} GB/day ({cdn_hit_rate*100:.0f}%)")
    print(f"    Origin serves:      {origin_bandwidth:>12,.1f} GB/day ({(1-cdn_hit_rate)*100:.0f}%)")
    print(f"    Total daily cost:   ${cdn_cost:>11,.2f}")
    print(f"    Total monthly:      ${cdn_cost * 30:>11,.2f}")
    print(f"")
    print(f"  SAVINGS:")
    print(f"    Daily:              ${savings:>11,.2f}")
    print(f"    Monthly:            ${savings * 30:>11,.2f}")
    print(f"    Origin load reduced by {cdn_hit_rate*100:.0f}%!")


# Small site
print(f"\n  --- Small Blog (100K views/day) ---")
calculate_cdn_impact(
    daily_page_views=100_000,
    assets_per_page=15,
    avg_asset_size_kb=100,
    cdn_hit_rate=0.90,
)

# Large site
print(f"\n  --- Large E-commerce (10M views/day) ---")
calculate_cdn_impact(
    daily_page_views=10_000_000,
    assets_per_page=30,
    avg_asset_size_kb=150,
    cdn_hit_rate=0.95,
)

print()


# ================================================================
# 5. CACHE INVALIDATION DEMO
# ================================================================

print("=" * 60)
print("  5. CACHE INVALIDATION STRATEGIES")
print("=" * 60)


def versioned_url(base_url: str, content: str) -> str:
    """Generate versioned URL using content hash."""
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    parts = base_url.rsplit(".", 1)
    return f"{parts[0]}.{content_hash}.{parts[1]}"


# Demonstrate versioned URLs
print(f"\n  --- Strategy: Versioned URLs ---")
v1 = versioned_url("/static/app.js", "console.log('version 1');")
v2 = versioned_url("/static/app.js", "console.log('version 2');")
v3 = versioned_url("/static/app.js", "console.log('version 2');")  # Same content = same hash

print(f"    Version 1: {v1}")
print(f"    Version 2: {v2}")
print(f"    Version 2 again: {v3} (same content = same hash!)")
print(f"    Different URL = cache miss = browser downloads fresh copy")

# TTL demo
print(f"\n  --- Strategy: TTL-based expiry ---")
print(f"    Cache-Control: max-age=300 (5 minutes)")
print(f"    t=0:    Content cached")
print(f"    t=60:   Still serving cached (4 min left)")
print(f"    t=300:  Cache EXPIRED, fetch fresh from origin")
print(f"    t=301:  New content cached for another 300s")

# Stale-while-revalidate
print(f"\n  --- Strategy: Stale-While-Revalidate ---")
print(f"    Cache-Control: max-age=60, stale-while-revalidate=3600")
print(f"    t=0:    Fresh content cached")
print(f"    t=30:   Serve from cache (still fresh)")
print(f"    t=61:   Cache 'stale' but STILL serves it instantly!")
print(f"            Background: fetches fresh copy from origin")
print(f"    t=62:   Fresh copy arrives, cache updated")
print(f"    Result: User NEVER waits. Always gets fast response.")


print("\n" + "=" * 60)
print("  System Design Topic 5 Complete!")
print("  Say 'next' for Topic 6: Load Balancers")
print("=" * 60)
