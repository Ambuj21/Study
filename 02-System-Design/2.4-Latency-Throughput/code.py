"""
System Design Topic 4 - Latency, Throughput & Estimation: Python Calculator

Demonstrates:
- Latency number visualization
- Interactive estimation calculator
- Worked examples: Twitter, YouTube, WhatsApp, URL Shortener
- QPS & storage calculator
- 80/20 cache sizing

Usage:
    python code.py
"""
import time
import math


# ================================================================
# 1. LATENCY NUMBERS — Visualized
# ================================================================

print("=" * 60)
print("  1. LATENCY NUMBERS — Every Programmer Must Know")
print("=" * 60)

latencies = [
    ("L1 cache read",              1,           "ns"),
    ("L2 cache read",              4,           "ns"),
    ("Branch mispredict",          5,           "ns"),
    ("Mutex lock/unlock",          25,          "ns"),
    ("RAM read",                   100,         "ns"),
    ("Compress 1KB (Snappy)",      3_000,       "ns"),
    ("Send 1KB over network",      10_000,      "ns"),
    ("SSD random read",            100_000,     "ns"),
    ("Read 1MB from RAM",          250_000,     "ns"),
    ("Same datacenter round trip", 500_000,     "ns"),
    ("Read 1MB from SSD",          1_000_000,   "ns"),
    ("HDD seek",                   10_000_000,  "ns"),
    ("Read 1MB from HDD",          20_000_000,  "ns"),
    ("Cross-continent round trip", 150_000_000, "ns"),
]

print(f"\n  {'Operation':<35} {'Time':>15} {'Relative':>10} {'Bar'}")
print(f"  {'─'*35} {'─'*15} {'─'*10} {'─'*30}")

max_log = math.log10(latencies[-1][1])

for name, ns, unit in latencies:
    # Format the time nicely
    if ns >= 1_000_000:
        time_str = f"{ns/1_000_000:.1f} ms"
    elif ns >= 1_000:
        time_str = f"{ns/1_000:.0f} us"
    else:
        time_str = f"{ns} ns"

    relative = f"{ns}x"
    bar_len = int((math.log10(max(ns, 1)) / max_log) * 25)
    bar = "█" * bar_len

    # Color-code by category
    if ns <= 100:
        bar = f"🟢 {bar}"
    elif ns <= 100_000:
        bar = f"🟡 {bar}"
    elif ns <= 1_000_000:
        bar = f"🟠 {bar}"
    else:
        bar = f"🔴 {bar}"

    print(f"  {name:<35} {time_str:>15} {relative:>10} {bar}")

# Key insights
print(f"""
  KEY INSIGHTS:
  ├── RAM is {100_000 // 100:,}x faster than SSD
  ├── SSD is {10_000_000 // 100_000:,}x faster than HDD
  ├── Same-DC is {150_000_000 // 500_000:,}x faster than cross-continent
  └── Compression (3 us) is almost free vs network (10 us)""")

print()


# ================================================================
# 2. POWERS OF 2 — Quick Reference
# ================================================================

print("=" * 60)
print("  2. POWERS OF 2 — Quick Reference")
print("=" * 60)

print(f"\n  {'Power':<8} {'Exact':>20} {'Approx':>15} {'Name':>8}")
print(f"  {'─'*8} {'─'*20} {'─'*15} {'─'*8}")

powers = [
    (10, "1 Thousand", "1 KB"),
    (20, "1 Million",  "1 MB"),
    (30, "1 Billion",  "1 GB"),
    (40, "1 Trillion", "1 TB"),
    (50, "1 Quadrillion", "1 PB"),
]

for power, approx, name in powers:
    exact = 2 ** power
    print(f"  2^{power:<5} {exact:>20,} {approx:>15} {name:>8}")

print()


# ================================================================
# 3. ESTIMATION CALCULATOR
# ================================================================

print("=" * 60)
print("  3. BACK-OF-ENVELOPE ESTIMATION CALCULATOR")
print("=" * 60)


def format_number(n: float) -> str:
    """Format large numbers with units."""
    if n >= 1e18:
        return f"{n/1e18:.1f} EB"
    elif n >= 1e15:
        return f"{n/1e15:.1f} PB"
    elif n >= 1e12:
        return f"{n/1e12:.1f} TB"
    elif n >= 1e9:
        return f"{n/1e9:.1f} GB"
    elif n >= 1e6:
        return f"{n/1e6:.1f} MB"
    elif n >= 1e3:
        return f"{n/1e3:.1f} KB"
    else:
        return f"{n:.0f} B"


def format_qps(qps: float) -> str:
    """Format QPS with units."""
    if qps >= 1e6:
        return f"{qps/1e6:.1f}M"
    elif qps >= 1e3:
        return f"{qps/1e3:.1f}K"
    else:
        return f"{qps:.0f}"


def estimate_system(
    name: str,
    total_users: int,
    dau: int,
    # Read side
    reads_per_user_per_day: int,
    avg_read_size_bytes: int,
    # Write side
    writes_per_user_per_day: float,
    avg_write_size_bytes: int,
    # Media
    media_write_ratio: float = 0,
    avg_media_size_bytes: int = 0,
    # Retention
    retention_days: int = 365 * 5,
    # Capacity
    qps_per_server: int = 5000,
):
    """Full back-of-envelope estimation."""

    SECONDS_PER_DAY = 86_400
    PEAK_FACTOR = 3

    # Daily volumes
    daily_writes = dau * writes_per_user_per_day
    daily_reads = dau * reads_per_user_per_day

    # QPS
    write_qps = daily_writes / SECONDS_PER_DAY
    read_qps = daily_reads / SECONDS_PER_DAY
    total_qps = write_qps + read_qps
    peak_qps = total_qps * PEAK_FACTOR

    # Storage per day
    text_storage_per_day = daily_writes * avg_write_size_bytes
    media_storage_per_day = daily_writes * media_write_ratio * avg_media_size_bytes
    total_storage_per_day = text_storage_per_day + media_storage_per_day
    total_storage_retention = total_storage_per_day * retention_days

    # Bandwidth (outgoing)
    read_bandwidth_per_day = daily_reads * avg_read_size_bytes
    read_bandwidth_per_day += daily_reads * media_write_ratio * avg_media_size_bytes * 0.5
    bandwidth_per_sec = read_bandwidth_per_day / SECONDS_PER_DAY

    # Servers
    servers_needed = math.ceil(peak_qps / qps_per_server)

    # Cache (80/20 rule)
    daily_hot_data = text_storage_per_day * 0.2  # Cache 20% of daily data
    cache_size = daily_hot_data * 30  # Keep 30 days of hot data cached

    # Read/Write ratio
    rw_ratio = read_qps / write_qps if write_qps > 0 else float('inf')

    print(f"\n  ╔{'═'*56}╗")
    print(f"  ║  {name:^54}║")
    print(f"  ╠{'═'*56}╣")
    print(f"  ║  {'Users & Scale':<54}║")
    print(f"  ║    Total Users:      {total_users:>18,}        ║")
    print(f"  ║    DAU:              {dau:>18,}        ║")
    print(f"  ║    Read/Write Ratio: {rw_ratio:>17.0f}:1        ║")
    print(f"  ╠{'═'*56}╣")
    print(f"  ║  {'QPS (Queries Per Second)':<54}║")
    print(f"  ║    Write QPS:        {format_qps(write_qps):>18}        ║")
    print(f"  ║    Read QPS:         {format_qps(read_qps):>18}        ║")
    print(f"  ║    Total QPS:        {format_qps(total_qps):>18}        ║")
    print(f"  ║    Peak QPS (3x):    {format_qps(peak_qps):>18}        ║")
    print(f"  ╠{'═'*56}╣")
    print(f"  ║  {'Storage':<54}║")
    print(f"  ║    Text/day:         {format_number(text_storage_per_day):>18}        ║")
    print(f"  ║    Media/day:        {format_number(media_storage_per_day):>18}        ║")
    print(f"  ║    Total/day:        {format_number(total_storage_per_day):>18}        ║")
    print(f"  ║    Retention ({retention_days} d): {format_number(total_storage_retention):>18}        ║")
    print(f"  ╠{'═'*56}╣")
    print(f"  ║  {'Infrastructure':<54}║")
    print(f"  ║    Bandwidth (out):  {format_number(bandwidth_per_sec):>18}/s      ║")
    print(f"  ║    Web servers:      {servers_needed:>18}        ║")
    print(f"  ║    Cache (Redis):    {format_number(cache_size):>18}        ║")
    print(f"  ╚{'═'*56}╝")


# ================================================================
# EXAMPLE 1: Twitter
# ================================================================

estimate_system(
    name="TWITTER",
    total_users=500_000_000,
    dau=200_000_000,
    reads_per_user_per_day=100,
    avg_read_size_bytes=500,
    writes_per_user_per_day=2,
    avg_write_size_bytes=500,
    media_write_ratio=0.1,
    avg_media_size_bytes=2_000_000,  # 2 MB
    retention_days=365 * 5,
    qps_per_server=5000,
)


# ================================================================
# EXAMPLE 2: YouTube
# ================================================================

estimate_system(
    name="YOUTUBE",
    total_users=2_000_000_000,
    dau=800_000_000,
    reads_per_user_per_day=5,     # 5 video plays
    avg_read_size_bytes=250_000_000,  # 250 MB per video (5 min @ 720p)
    writes_per_user_per_day=0.01,    # 1% of DAU uploads
    avg_write_size_bytes=500,         # metadata
    media_write_ratio=1.0,
    avg_media_size_bytes=250_000_000,  # 250 MB per video
    retention_days=365 * 10,          # keep forever (~10 years)
    qps_per_server=2000,
)


# ================================================================
# EXAMPLE 3: WhatsApp
# ================================================================

estimate_system(
    name="WHATSAPP (Chat App)",
    total_users=2_000_000_000,
    dau=700_000_000,
    reads_per_user_per_day=50,     # read ~50 messages
    avg_read_size_bytes=200,
    writes_per_user_per_day=50,    # send ~50 messages
    avg_write_size_bytes=200,
    media_write_ratio=0.05,
    avg_media_size_bytes=300_000,   # 300 KB compressed image
    retention_days=30,             # 30 day retention
    qps_per_server=5000,
)


# ================================================================
# EXAMPLE 4: URL Shortener
# ================================================================

estimate_system(
    name="URL SHORTENER (bit.ly)",
    total_users=100_000_000,
    dau=10_000_000,
    reads_per_user_per_day=10,     # 10 clicks on short URLs
    avg_read_size_bytes=500,       # redirect response
    writes_per_user_per_day=0.3,   # ~3M new URLs/day
    avg_write_size_bytes=500,      # original URL + metadata
    retention_days=365 * 5,
    qps_per_server=10000,          # simple redirect is fast
)

print()


# ================================================================
# 4. CACHE SIZING — 80/20 Rule
# ================================================================

print("=" * 60)
print("  4. CACHE SIZING — The 80/20 Rule")
print("=" * 60)


def cache_impact(
    total_data_gb: float,
    cache_percent: float,
    db_latency_ms: float = 10.0,
    cache_latency_ms: float = 0.1,
    total_requests: int = 100_000,
):
    """Show the impact of caching different percentages of data."""
    cache_size_gb = total_data_gb * (cache_percent / 100)

    # With Zipf distribution, caching 20% covers ~80% of requests
    if cache_percent >= 50:
        hit_rate = min(99.5, 60 + cache_percent * 0.8)
    elif cache_percent >= 20:
        hit_rate = 40 + cache_percent * 2
    else:
        hit_rate = cache_percent * 3.5

    hit_rate = min(hit_rate, 99.9)

    cache_hits = int(total_requests * hit_rate / 100)
    cache_misses = total_requests - cache_hits

    avg_latency = (cache_hits * cache_latency_ms + cache_misses * db_latency_ms) / total_requests
    speedup = db_latency_ms / avg_latency

    return cache_size_gb, hit_rate, avg_latency, speedup


total_db = 500  # 500 GB database

print(f"\n  Database size: {total_db} GB")
print(f"  DB latency: 10ms | Cache latency: 0.1ms")
print(f"\n  {'Cache %':>8} {'Cache Size':>12} {'Hit Rate':>10} {'Avg Latency':>13} {'Speedup':>10}")
print(f"  {'─'*8} {'─'*12} {'─'*10} {'─'*13} {'─'*10}")

for pct in [1, 5, 10, 20, 30, 50, 80]:
    size, hit, lat, speed = cache_impact(total_db, pct)
    print(f"  {pct:>7}% {size:>10.0f} GB {hit:>9.1f}% {lat:>11.2f} ms {speed:>9.1f}x")

print(f"""
  INSIGHT: Caching just 20% of data gives ~80% hit rate
  and makes the system ~5x faster!
  Diminishing returns after ~30% — don't cache everything.""")

print()


# ================================================================
# 5. PEAK vs AVERAGE TRAFFIC
# ================================================================

print("=" * 60)
print("  5. PEAK vs AVERAGE — Why it matters for capacity")
print("=" * 60)

avg_qps = 10_000

print(f"\n  Average QPS: {avg_qps:,}")
print(f"\n  {'Time':>12} {'Factor':>8} {'QPS':>10} {'Servers (@5K QPS)':>20}")
print(f"  {'─'*12} {'─'*8} {'─'*10} {'─'*20}")

periods = [
    ("3am", 0.1),
    ("7am", 0.5),
    ("10am", 1.2),
    ("12pm (lunch)", 2.0),
    ("3pm", 1.5),
    ("7pm (evening)", 3.0),
    ("9pm (PEAK)", 3.5),
    ("11pm", 1.0),
]

for period, factor in periods:
    qps = int(avg_qps * factor)
    servers = math.ceil(qps / 5000)
    bar = "█" * servers + "░" * (8 - servers)
    print(f"  {period:>12} {factor:>7.1f}x {qps:>10,} {servers:>8} servers  {bar}")

print(f"""
  WARNING: If you provision for AVERAGE ({avg_qps:,} QPS = {avg_qps//5000} servers),
  your system CRASHES at peak ({int(avg_qps*3.5):,} QPS needs {math.ceil(avg_qps*3.5/5000)} servers)!

  RULE: Always provision for peak (3-4x average)
  BETTER: Use auto-scaling to handle peaks dynamically""")


print("\n" + "=" * 60)
print("  System Design Topic 4 Complete!")
print("  Stage 1 (Foundation) COMPLETE!")
print("  Say 'next' for Stage 2, Topic 5: DNS & CDN")
print("=" * 60)
