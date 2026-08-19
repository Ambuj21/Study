# 📘 Topic 1.3 — How the Internet Actually Works

> **Why this matters**: As a backend developer, every line of code you write will eventually serve a request that traveled through **DNS, TCP, HTTP, and multiple servers**. If you don't understand this journey, you'll write slow, insecure, broken APIs without knowing why.

> **Code Implementation**: See [code.py](./code.py) for runnable Python implementation

---

## 🧠 The Big Picture — What Happens When You Type a URL?

```mermaid
sequenceDiagram
    actor You
    participant Browser
    participant DNS as DNS Server
    participant ISP as ISP / Internet
    participant Server as Web Server
    participant App as Backend App
    participant DB as Database

    You->>Browser: Type "www.google.com"
    Browser->>DNS: What's the IP for google.com?
    DNS-->>Browser: It's 142.250.190.78

    Browser->>ISP: Connect to 142.250.190.78
    ISP->>Server: Route packets across the internet

    Note over Browser, Server: TCP 3-Way Handshake
    Browser->>Server: SYN (Hey, want to connect?)
    Server-->>Browser: SYN-ACK (Sure, let's connect!)
    Browser->>Server: ACK (Great, we're connected!)

    Note over Browser, Server: TLS/SSL Handshake (for HTTPS)
    Browser->>Server: ClientHello (encryption negotiation)
    Server-->>Browser: Certificate + ServerHello
    Browser->>Server: Key Exchange (encrypted tunnel ready)

    Browser->>Server: GET /search?q=python HTTP/1.1
    Server->>App: Forward request
    App->>DB: Query data
    DB-->>App: Results
    App-->>Server: HTML Response
    Server-->>Browser: HTTP 200 OK + HTML
    Browser-->>You: Rendered webpage!
```

> This entire process happens in **~200-500 milliseconds**. Let's break down each step.

---

## 1️⃣ DNS — The Internet's Phone Book

### 🎯 Analogy
> You know your friend's name ("google.com") but not their address (IP). DNS is like calling **directory assistance** — you give a name, they give you the number.

### 📊 DNS Resolution Flow

```mermaid
graph TD
    Browser["🌐 Browser<br/>Where is google.com?"] --> Cache{"🗄️ Local Cache?"}
    Cache -->|HIT| Done["✅ Got IP: 142.250.190.78"]
    Cache -->|MISS| Resolver["📞 ISP DNS Resolver"]

    Resolver --> Root["🌍 Root DNS Server<br/>'I know who handles .com'"]
    Root --> TLD["📂 .com TLD Server<br/>'I know who handles google.com'"]
    TLD --> Auth["🏢 Google's DNS Server<br/>'google.com = 142.250.190.78'"]
    Auth --> Resolver
    Resolver --> Done

    style Browser fill:#4d96ff,stroke:#333,color:#fff
    style Cache fill:#ffd93d,stroke:#333,color:#333
    style Root fill:#e74c3c,stroke:#333,color:#fff
    style TLD fill:#e67e22,stroke:#333,color:#fff
    style Auth fill:#2ecc71,stroke:#333,color:#fff
    style Done fill:#2ecc71,stroke:#333,color:#fff,stroke-width:3px
```

### Pseudo Code

```
FUNCTION resolve_dns(domain):
    // Step 1: Check local cache
    IF domain IN local_cache:
        RETURN local_cache[domain]

    // Step 2: Ask ISP's recursive resolver
    resolver = ISP_DNS_RESOLVER

    // Step 3: Resolver walks the DNS tree
    root_server = resolver.ask_root("Where is .com?")
    tld_server  = root_server.ask("Where is google.com?")
    ip_address  = tld_server.ask("What is google.com's IP?")

    // Step 4: Cache it for next time (TTL = Time To Live)
    local_cache[domain] = ip_address  // expires after TTL
    RETURN ip_address
```

### Key Concepts

| Concept | What It Means |
|---------|--------------|
| **A Record** | Maps domain → IPv4 address (e.g., google.com → 142.250.190.78) |
| **CNAME** | Maps domain → another domain (e.g., www.google.com → google.com) |
| **TTL** | How long to cache the result (e.g., 300 seconds) |
| **NS Record** | Points to the authoritative name server for a domain |

---

## 2️⃣ TCP — The Reliable Delivery Truck

### 🎯 Analogy
> TCP is like sending a **registered letter**. You get confirmation it arrived, it arrives in order, and if a piece is missing, it's resent. UDP is like shouting across a room — fast but no guarantee anyone heard.

### 📊 TCP 3-Way Handshake

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    Note over C,S: Connection Establishment
    C->>S: SYN (seq=100)<br/>"Hey, I want to talk"
    S-->>C: SYN-ACK (seq=300, ack=101)<br/>"OK, I'm listening"
    C->>S: ACK (ack=301)<br/>"Great, let's go!"

    Note over C,S: Data Transfer
    C->>S: Data Packet 1 (seq=101)
    S-->>C: ACK (ack=201) "Got it"
    C->>S: Data Packet 2 (seq=201)
    S-->>C: ACK (ack=301) "Got it"

    Note over C,S: Connection Teardown
    C->>S: FIN "I'm done"
    S-->>C: ACK "OK"
    S-->>C: FIN "Me too"
    C->>S: ACK "Goodbye"
```

### Pseudo Code

```
FUNCTION tcp_connect(client, server):
    // 3-Way Handshake
    client.send(SYN, seq=random_number)
    response = server.receive()       // Server responds with SYN-ACK
    client.send(ACK, ack=response.seq + 1)

    // Connection established! Now send data
    WHILE has_data_to_send:
        packet = next_packet()
        client.send(packet)

        IF NOT received_ack(timeout=2s):
            client.resend(packet)     // TCP guarantees delivery!

    // Teardown
    client.send(FIN)
    server.send(ACK)
    server.send(FIN)
    client.send(ACK)
```

### TCP vs UDP — When to Use Which

```mermaid
graph TD
    Q{"What are you<br/>building?"}
    Q -->|"Need reliability<br/>& ordering"| TCP["🔒 TCP"]
    Q -->|"Need speed,<br/>OK to lose some data"| UDP["⚡ UDP"]

    TCP --> T1["Web pages (HTTP)"]
    TCP --> T2["Email (SMTP)"]
    TCP --> T3["File transfer (FTP)"]
    TCP --> T4["Database connections"]

    UDP --> U1["Video streaming"]
    UDP --> U2["Online gaming"]
    UDP --> U3["DNS lookups"]
    UDP --> U4["Voice calls (VoIP)"]

    style TCP fill:#3498db,stroke:#333,color:#fff
    style UDP fill:#e74c3c,stroke:#333,color:#fff
```

| Feature | TCP | UDP |
|---------|-----|-----|
| **Reliable?** | Yes — resends lost packets | No — fire and forget |
| **Ordered?** | Yes — packets arrive in order | No — can arrive out of order |
| **Speed** | Slower (handshake overhead) | Faster (no handshake) |
| **Use Case** | HTTP, Email, Databases | Video, Gaming, DNS |

---

## 3️⃣ HTTP / HTTPS — The Language of the Web

### 🎯 Analogy
> HTTP is the **language** that browsers and servers speak. Like a restaurant: the browser is the customer, the HTTP request is the order, and the HTTP response is the food.

### 📊 Anatomy of an HTTP Request

```mermaid
graph TD
    subgraph "📤 HTTP REQUEST"
        A["METHOD: GET, POST, PUT, DELETE"]
        B["URL: /api/users/123"]
        C["HEADERS:<br/>Content-Type: application/json<br/>Authorization: Bearer token123<br/>Accept: application/json"]
        D["BODY (for POST/PUT):<br/>{name: 'Alice', age: 28}"]
    end

    subgraph "📥 HTTP RESPONSE"
        E["STATUS CODE: 200 OK"]
        F["HEADERS:<br/>Content-Type: application/json<br/>Cache-Control: max-age=3600"]
        G["BODY:<br/>{id: 123, name: 'Alice', age: 28}"]
    end

    A --> E

    style A fill:#4d96ff,stroke:#333,color:#fff
    style E fill:#2ecc71,stroke:#333,color:#fff
```

### HTTP Methods — The CRUD Operations

```mermaid
graph LR
    subgraph "HTTP Methods = CRUD"
        GET["GET<br/>📖 READ<br/>Get user data"]
        POST["POST<br/>✏️ CREATE<br/>Create new user"]
        PUT["PUT<br/>🔄 UPDATE<br/>Replace user data"]
        PATCH["PATCH<br/>🩹 PARTIAL UPDATE<br/>Update user email"]
        DELETE["DELETE<br/>🗑️ DELETE<br/>Remove user"]
    end

    style GET fill:#2ecc71,stroke:#333,color:#fff
    style POST fill:#3498db,stroke:#333,color:#fff
    style PUT fill:#f39c12,stroke:#333,color:#fff
    style PATCH fill:#e67e22,stroke:#333,color:#fff
    style DELETE fill:#e74c3c,stroke:#333,color:#fff
```

### Pseudo Code — How a Server Handles Requests

```
FUNCTION handle_request(request):
    // Step 1: Parse the request
    method = request.method      // GET, POST, PUT, DELETE
    path   = request.url         // /api/users/123
    headers = request.headers    // Authorization, Content-Type
    body   = request.body        // JSON data (for POST/PUT)

    // Step 2: Authentication
    token = headers["Authorization"]
    user = verify_token(token)
    IF user IS NULL:
        RETURN Response(status=401, body="Unauthorized")

    // Step 3: Route to the right handler
    IF method == "GET" AND path == "/api/users/{id}":
        user_data = database.find_user(id)
        IF user_data IS NULL:
            RETURN Response(status=404, body="User not found")
        RETURN Response(status=200, body=user_data)

    ELSE IF method == "POST" AND path == "/api/users":
        new_user = database.create_user(body)
        RETURN Response(status=201, body=new_user)

    ELSE IF method == "DELETE" AND path == "/api/users/{id}":
        database.delete_user(id)
        RETURN Response(status=204, body=null)

    ELSE:
        RETURN Response(status=404, body="Route not found")
```

### HTTP Status Codes — What They Mean

```mermaid
graph TD
    subgraph "🟢 2xx — Success"
        S200["200 OK — Everything worked"]
        S201["201 Created — New resource made"]
        S204["204 No Content — Deleted successfully"]
    end

    subgraph "🟡 3xx — Redirect"
        S301["301 Moved — URL changed permanently"]
        S304["304 Not Modified — Use your cache"]
    end

    subgraph "🔴 4xx — Client Error (YOUR fault)"
        S400["400 Bad Request — Invalid data sent"]
        S401["401 Unauthorized — Not logged in"]
        S403["403 Forbidden — No permission"]
        S404["404 Not Found — Doesn't exist"]
        S429["429 Too Many Requests — Rate limited"]
    end

    subgraph "💀 5xx — Server Error (SERVER's fault)"
        S500["500 Internal Error — Server crashed"]
        S502["502 Bad Gateway — Upstream server down"]
        S503["503 Unavailable — Server overloaded"]
    end

    style S200 fill:#2ecc71,stroke:#333,color:#fff
    style S201 fill:#2ecc71,stroke:#333,color:#fff
    style S301 fill:#f1c40f,stroke:#333,color:#333
    style S400 fill:#e74c3c,stroke:#333,color:#fff
    style S401 fill:#e74c3c,stroke:#333,color:#fff
    style S404 fill:#e74c3c,stroke:#333,color:#fff
    style S500 fill:#7f0000,stroke:#333,color:#fff
    style S503 fill:#7f0000,stroke:#333,color:#fff
```

---

## 4️⃣ HTTPS & TLS — The Encrypted Tunnel

### 🎯 Analogy
> HTTP is like sending a **postcard** — anyone can read it. HTTPS is like putting your message in a **locked box** where only the receiver has the key.

### 📊 TLS Handshake Flow

```mermaid
sequenceDiagram
    participant B as Browser
    participant S as Server

    B->>S: ClientHello<br/>"I support TLS 1.3, these ciphers..."
    S-->>B: ServerHello + Certificate<br/>"Let's use TLS 1.3, here's my cert"

    Note over B: Browser verifies certificate<br/>with Certificate Authority (CA)

    B->>S: Key Exchange<br/>"Here's my part of the shared secret"
    S-->>B: Key Exchange<br/>"Here's my part"

    Note over B,S: Both compute the SAME<br/>symmetric encryption key

    B->>S: 🔒 Encrypted request<br/>GET /api/users
    S-->>B: 🔒 Encrypted response<br/>200 OK + data
```

### Pseudo Code

```
FUNCTION tls_handshake(client, server):
    // Step 1: Client says hello
    client_hello = {
        tls_version: "1.3",
        supported_ciphers: ["AES-256-GCM", "ChaCha20"],
        random: generate_random_bytes()
    }
    client.send(client_hello)

    // Step 2: Server responds with certificate
    server_hello = {
        chosen_cipher: "AES-256-GCM",
        certificate: server.ssl_certificate,
        random: generate_random_bytes()
    }
    server.send(server_hello)

    // Step 3: Client verifies certificate
    is_valid = verify_with_CA(server_hello.certificate)
    IF NOT is_valid:
        ABORT "Certificate not trusted!"

    // Step 4: Key exchange (Diffie-Hellman)
    shared_secret = diffie_hellman_exchange(client, server)

    // Step 5: Both derive the same symmetric key
    session_key = derive_key(shared_secret)

    // Now all communication is encrypted with session_key!
    RETURN encrypted_connection(session_key)
```

---

## 5️⃣ REST vs GraphQL vs gRPC vs WebSocket

### 📊 Comparison

```mermaid
graph TD
    subgraph "🌐 API Communication Styles"
        REST["REST<br/>📦 Resource-based<br/>GET /users/123"]
        GQL["GraphQL<br/>🎯 Query exactly what you need<br/>query { user(id:123) { name } }"]
        GRPC["gRPC<br/>⚡ Binary, super fast<br/>Microservice-to-microservice"]
        WS["WebSocket<br/>🔄 Real-time, bidirectional<br/>Chat, live updates"]
    end

    REST ---|"Most common<br/>for public APIs"| USE1["Web/Mobile Apps"]
    GQL ---|"Flexible queries<br/>avoid over-fetching"| USE2["Complex UIs"]
    GRPC ---|"High performance<br/>strongly typed"| USE3["Internal Services"]
    WS ---|"Persistent connection<br/>server can push"| USE4["Real-time Apps"]

    style REST fill:#3498db,stroke:#333,color:#fff
    style GQL fill:#e535ab,stroke:#333,color:#fff
    style GRPC fill:#2ecc71,stroke:#333,color:#fff
    style WS fill:#f39c12,stroke:#333,color:#fff
```

| Feature | REST | GraphQL | gRPC | WebSocket |
|---------|------|---------|------|-----------|
| **Protocol** | HTTP | HTTP | HTTP/2 | TCP |
| **Data Format** | JSON | JSON | Protobuf (binary) | Any |
| **Speed** | Good | Good | Fastest | Real-time |
| **Over-fetching** | Common | Never | Never | N/A |
| **Best For** | Public APIs | Complex UIs | Microservices | Chat, Gaming |
| **Learning Curve** | Easy | Medium | Hard | Medium |

### Pseudo Code — REST vs GraphQL

```
// ═══ REST: Multiple requests to get what you need ═══
// Problem: You want user name + their posts + their followers

GET /api/users/123           → { id: 123, name: "Alice", email: "...", age: 28, ... }
GET /api/users/123/posts     → [{ title: "...", body: "..." }, ...]
GET /api/users/123/followers → [{ id: 456, name: "Bob" }, ...]

// 3 requests! And you got extra fields you don't need (over-fetching)


// ═══ GraphQL: ONE request, get exactly what you need ═══
POST /graphql
{
    query {
        user(id: 123) {
            name                    // Only the fields you want
            posts { title }         // Only title, not body
            followers { name }      // Only name, not id
        }
    }
}
// 1 request! No over-fetching!
```

---

## 6️⃣ Ports — The Apartment Numbers

### 🎯 Analogy
> An IP address is like a **building address**. A port is like an **apartment number**. Multiple services (apartments) can live on the same server (building).

```mermaid
graph TD
    subgraph "🏢 Server: 142.250.190.78"
        P80["Port 80<br/>🌐 HTTP"]
        P443["Port 443<br/>🔒 HTTPS"]
        P22["Port 22<br/>🖥️ SSH"]
        P5432["Port 5432<br/>🗄️ PostgreSQL"]
        P6379["Port 6379<br/>⚡ Redis"]
        P8000["Port 8000<br/>🐍 FastAPI"]
    end

    style P80 fill:#3498db,stroke:#333,color:#fff
    style P443 fill:#2ecc71,stroke:#333,color:#fff
    style P22 fill:#9b59b6,stroke:#333,color:#fff
    style P5432 fill:#e74c3c,stroke:#333,color:#fff
    style P6379 fill:#e67e22,stroke:#333,color:#fff
    style P8000 fill:#1abc9c,stroke:#333,color:#fff
```

### Common Ports to Know

| Port | Service | What It Does |
|------|---------|-------------|
| 80 | HTTP | Unencrypted web traffic |
| 443 | HTTPS | Encrypted web traffic |
| 22 | SSH | Remote server access |
| 5432 | PostgreSQL | Database connections |
| 3306 | MySQL | Database connections |
| 27017 | MongoDB | Database connections |
| 6379 | Redis | Cache/message broker |
| 8000/8080 | Dev servers | FastAPI, Spring Boot, etc. |

---

## 🏋️ Practice Exercises

### Exercise 1: Trace the Request
> Describe every step that happens when you type `https://api.github.com/users/torvalds` in your browser. Include DNS, TCP, TLS, and HTTP.

### Exercise 2: Status Code Quiz
> What status code should your API return for:
> - User tries to log in with wrong password?
> - User requests their own profile successfully?
> - User tries to access admin panel without permission?
> - Server's database connection crashes?

### Exercise 3: REST vs GraphQL
> Your app has Users, Posts, and Comments. A mobile app needs to show a user profile with their 5 latest posts and comment count per post. Design the REST endpoints AND the GraphQL query. Which is better here and why?

---

## 🎤 Interview Corner

> **Q: "What happens when you type google.com in the browser?"**
> This is the **#1 most asked** system design warmup question. Walk through: DNS → TCP → TLS → HTTP → Server → Response → Rendering.

> **Q: "What's the difference between HTTP and HTTPS?"**
> "HTTPS adds TLS encryption on top of HTTP. It prevents man-in-the-middle attacks, ensures data integrity, and verifies the server's identity through certificates."

> **Q: "When would you choose WebSockets over REST?"**
> "When the server needs to push data to the client without being asked — like chat messages, live notifications, stock price tickers, or multiplayer game state."

---

## ✅ Key Takeaways

| Concept | Remember |
|---------|----------|
| **DNS** | Translates domain names to IP addresses |
| **TCP** | Reliable, ordered delivery with handshake |
| **UDP** | Fast, unreliable, for video/gaming |
| **HTTP** | Request-response protocol with methods & status codes |
| **HTTPS/TLS** | Encrypted HTTP using certificates |
| **REST** | Resource-based, most common API style |
| **Ports** | Different services on the same machine |

---

**Next up → [Topic 1.4: Database Fundamentals](../1.4-Database-Fundamentals/)**
