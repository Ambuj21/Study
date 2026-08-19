"""
Topic 1.3 - How the Internet Actually Works: Python Code

This file demonstrates DNS resolution, TCP connections, HTTP requests,
and different API styles using real Python code you can run.

Usage:
    pip install requests
    python code.py
"""
import socket
import time
import json


# ================================================================
# 1. DNS RESOLUTION - See it happen in real time
# ================================================================

print("=" * 60)
print("  1. DNS RESOLUTION")
print("=" * 60)


def resolve_dns(domain):
    """Resolve a domain name to IP address (what DNS does)."""
    print(f"\n  Resolving: {domain}")

    start = time.perf_counter()
    try:
        # socket.getaddrinfo gives us ALL the info
        results = socket.getaddrinfo(domain, 443)  # port 443 = HTTPS
        ip = results[0][4][0]
        elapsed = (time.perf_counter() - start) * 1000

        print(f"  IP Address: {ip}")
        print(f"  Time: {elapsed:.2f}ms")

        # Second lookup should be cached (faster)
        start2 = time.perf_counter()
        socket.getaddrinfo(domain, 443)
        elapsed2 = (time.perf_counter() - start2) * 1000
        print(f"  Cached lookup: {elapsed2:.2f}ms (should be faster!)")

        return ip
    except socket.gaierror as e:
        print(f"  DNS Error: {e}")
        return None


# Resolve some popular domains
for domain in ["google.com", "github.com", "python.org"]:
    resolve_dns(domain)

print()


# ================================================================
# 2. TCP CONNECTION - The 3-Way Handshake
# ================================================================

print("=" * 60)
print("  2. TCP CONNECTION (Raw Socket)")
print("=" * 60)


def tcp_connect_demo(host, port):
    """Demonstrate a raw TCP connection."""
    print(f"\n  Connecting to {host}:{port}...")

    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        start = time.perf_counter()
        # .connect() performs the 3-way handshake (SYN, SYN-ACK, ACK)
        sock.connect((host, port))
        elapsed = (time.perf_counter() - start) * 1000

        print(f"  Connected! (3-way handshake completed)")
        print(f"  Handshake time: {elapsed:.2f}ms")
        print(f"  Local address: {sock.getsockname()}")
        print(f"  Remote address: {sock.getpeername()}")

        sock.close()
        print(f"  Connection closed (FIN sent)")
    except Exception as e:
        print(f"  Connection failed: {e}")


tcp_connect_demo("google.com", 80)

print()


# ================================================================
# 3. RAW HTTP REQUEST - Build it from scratch
# ================================================================

print("=" * 60)
print("  3. RAW HTTP REQUEST (Manual)")
print("=" * 60)


def raw_http_get(host, path="/"):
    """Send a raw HTTP GET request using TCP sockets."""
    print(f"\n  Sending GET {path} to {host}")

    # Build the HTTP request manually
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Connection: close\r\n"
        f"User-Agent: PythonLearner/1.0\r\n"
        f"\r\n"  # Empty line = end of headers
    )

    print(f"  --- Request ---")
    for line in request.strip().split("\r\n"):
        print(f"  > {line}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, 80))
        sock.send(request.encode())

        # Receive response
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        sock.close()

        # Parse response
        response_text = response.decode("utf-8", errors="replace")
        headers, _, body = response_text.partition("\r\n\r\n")

        print(f"\n  --- Response Headers ---")
        for line in headers.split("\r\n")[:6]:
            print(f"  < {line}")

        print(f"\n  Body length: {len(body)} characters")
        print(f"  First 200 chars: {body[:200]}...")

    except Exception as e:
        print(f"  Error: {e}")


raw_http_get("httpbin.org", "/get")

print()


# ================================================================
# 4. HTTP with requests library (The Easy Way)
# ================================================================

print("=" * 60)
print("  4. HTTP METHODS with 'requests' library")
print("=" * 60)

try:
    import requests

    base_url = "https://jsonplaceholder.typicode.com"

    # --- GET: Read data ---
    print("\n  --- GET /users/1 ---")
    response = requests.get(f"{base_url}/users/1")
    print(f"  Status: {response.status_code}")
    user = response.json()
    print(f"  User: {user['name']} ({user['email']})")

    # --- POST: Create data ---
    print("\n  --- POST /posts ---")
    new_post = {
        "title": "Learning HTTP Methods",
        "body": "Understanding how the internet works!",
        "userId": 1
    }
    response = requests.post(f"{base_url}/posts", json=new_post)
    print(f"  Status: {response.status_code} (201 = Created)")
    print(f"  Created: {response.json()}")

    # --- PUT: Replace data ---
    print("\n  --- PUT /posts/1 ---")
    updated_post = {
        "title": "Updated Title",
        "body": "Updated body content",
        "userId": 1
    }
    response = requests.put(f"{base_url}/posts/1", json=updated_post)
    print(f"  Status: {response.status_code}")
    print(f"  Updated: {response.json()['title']}")

    # --- DELETE: Remove data ---
    print("\n  --- DELETE /posts/1 ---")
    response = requests.delete(f"{base_url}/posts/1")
    print(f"  Status: {response.status_code} (200 = Deleted)")

    # --- Inspect headers ---
    print("\n  --- Response Headers ---")
    response = requests.get(f"{base_url}/users/1")
    for key, value in list(response.headers.items())[:5]:
        print(f"  {key}: {value}")

except ImportError:
    print("  'requests' not installed. Run: pip install requests")

print()


# ================================================================
# 5. HTTP Status Codes - Quick Reference
# ================================================================

print("=" * 60)
print("  5. HTTP STATUS CODES")
print("=" * 60)

status_codes = {
    "2xx Success": {
        200: "OK - Request succeeded",
        201: "Created - New resource created",
        204: "No Content - Deleted successfully",
    },
    "3xx Redirect": {
        301: "Moved Permanently - URL changed",
        304: "Not Modified - Use cached version",
    },
    "4xx Client Error": {
        400: "Bad Request - Invalid data sent",
        401: "Unauthorized - Not logged in",
        403: "Forbidden - No permission",
        404: "Not Found - Resource doesn't exist",
        429: "Too Many Requests - Rate limited",
    },
    "5xx Server Error": {
        500: "Internal Server Error - Server crashed",
        502: "Bad Gateway - Upstream failure",
        503: "Service Unavailable - Overloaded",
    }
}

for category, codes in status_codes.items():
    print(f"\n  {category}:")
    for code, desc in codes.items():
        print(f"    {code}: {desc}")

print()


# ================================================================
# 6. PORT SCANNING - See what's running locally
# ================================================================

print("=" * 60)
print("  6. PORT SCANNER - What's running on localhost?")
print("=" * 60)

common_ports = {
    80: "HTTP",
    443: "HTTPS",
    3000: "Node.js / React Dev Server",
    3306: "MySQL",
    5000: "Flask",
    5432: "PostgreSQL",
    6379: "Redis",
    8000: "FastAPI / Django",
    8080: "HTTP Alt / Tomcat",
    8888: "Jupyter Notebook",
    27017: "MongoDB",
}

print(f"\n  Scanning localhost for common services...")
open_ports = []

for port, service in common_ports.items():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.1)
    result = sock.connect_ex(("127.0.0.1", port))
    if result == 0:
        open_ports.append((port, service))
        print(f"    Port {port:>5} OPEN  - {service}")
    sock.close()

if not open_ports:
    print(f"    No common ports are open on localhost")
else:
    print(f"\n  Found {len(open_ports)} open port(s)")

print()
print("=" * 60)
print("  Topic 1.3 Complete!")
print("  Say 'next' for Topic 1.4: Database Fundamentals")
print("=" * 60)
