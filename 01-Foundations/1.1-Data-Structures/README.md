# 📘 Topic 1.1 — Data Structures & When to Use Them

> **Why this matters**: Data structures are the **containers** that hold your data. Choosing the wrong one is like using a suitcase to carry water — it technically holds stuff, but it's the wrong tool. The right data structure makes your code **10x-100x faster**.

> **Code Implementation**: See [code.py](./code.py) for runnable Python implementation

---

## 🧠 The Big Picture — What Are Data Structures?

Think of data structures as **different types of shelves** in a warehouse:

```mermaid
graph LR
    subgraph "🏠 Your Program"
        A["📦 Data<br/>(users, orders, messages)"]
    end

    A --> B["Which container<br/>should I use?"]

    B --> C["📋 Array/List<br/>Ordered shelf"]
    B --> D["🗂️ Hash Map/Dict<br/>Filing cabinet"]
    B --> E["📚 Stack<br/>Pile of books"]
    B --> F["🎟️ Queue<br/>Movie ticket line"]
    B --> G["🌳 Tree<br/>Family tree"]
    B --> H["⛰️ Heap<br/>Priority system"]

    style A fill:#ff6b6b,stroke:#333,color:#fff
    style B fill:#ffd93d,stroke:#333,color:#333
    style C fill:#4d96ff,stroke:#333,color:#fff
    style D fill:#6bcb77,stroke:#333,color:#fff
    style E fill:#9b59b6,stroke:#333,color:#fff
    style F fill:#e67e22,stroke:#333,color:#fff
    style G fill:#1abc9c,stroke:#333,color:#fff
    style H fill:#e74c3c,stroke:#333,color:#fff
```

---

## 1️⃣ Arrays & Lists — The Ordered Shelf

### 🎯 Real-World Analogy
> Imagine a **row of lockers** numbered 0, 1, 2, 3... You can instantly go to locker #5, but if you want to insert a new locker between #2 and #3, you have to **shift everything after it**.

### 📊 How It Looks in Memory

```mermaid
graph LR
    subgraph "📋 List: ['apple', 'banana', 'cherry', 'date']"
        I0["Index 0<br/>🍎 'apple'"]
        I1["Index 1<br/>🍌 'banana'"]
        I2["Index 2<br/>🍒 'cherry'"]
        I3["Index 3<br/>🌴 'date'"]
    end

    I0 --> I1 --> I2 --> I3

    style I0 fill:#4d96ff,stroke:#333,color:#fff
    style I1 fill:#4d96ff,stroke:#333,color:#fff
    style I2 fill:#4d96ff,stroke:#333,color:#fff
    style I3 fill:#4d96ff,stroke:#333,color:#fff
```

### Pseudo Code

```
// Creating a list
fruits = ["apple", "banana", "cherry", "date"]

// Access by index — INSTANT O(1)
item = fruits[2]                    // "cherry" — jumps directly to position 2

// Append at end — FAST O(1)
APPEND(fruits, "elderberry")

// Insert in middle — SLOW O(n) — shifts everything after!
INSERT(fruits, position=1, value="blueberry")
// Now: ["apple", "blueberry", "banana", "cherry", "date", "elderberry"]

// Search by value — SLOW O(n) — checks one by one
found = SEARCH(fruits, "cherry")    // True, but scanned through the list

// Transform each element
prices = [10, 20, 30, 40]
discounted = []
FOR EACH price IN prices:
    APPEND(discounted, price * 0.9)
// discounted = [9.0, 18.0, 27.0, 36.0]
```

### ✅ Use Lists When:
- You need **ordered** data
- You access elements by **position/index**
- You mostly **append** to the end
- Example: list of recent orders, playlist of songs

### ❌ Don't Use Lists When:
- You need to **search** frequently (use a hash map/set instead)
- You **insert/delete** in the middle often (use a linked list)

---

## 2️⃣ Hash Map / Dictionary — The Filing Cabinet

### 🎯 Real-World Analogy
> Imagine a **filing cabinet** where each drawer has a **label** (key). You say "give me the drawer labeled 'John'" and you get it **instantly**. No searching through drawers one by one.

### 📊 How It Works Inside

```mermaid
graph TD
    subgraph "🔑 Keys go through a Hash Function"
        K1["'alice'"] -->|hash| H["⚙️ Hash Function<br/>Converts key → number"]
        K2["'bob'"] -->|hash| H
        K3["'charlie'"] -->|hash| H
    end

    subgraph "📦 Values stored in buckets"
        H -->|bucket 2| B2["alice → 'alice@email.com'"]
        H -->|bucket 5| B5["bob → 'bob@email.com'"]
        H -->|bucket 1| B1["charlie → 'charlie@email.com'"]
    end

    style H fill:#e74c3c,stroke:#333,color:#fff,stroke-width:3px
    style B2 fill:#6bcb77,stroke:#333,color:#fff
    style B5 fill:#6bcb77,stroke:#333,color:#fff
    style B1 fill:#6bcb77,stroke:#333,color:#fff
```

> The **hash function** is the magic. It converts any key into a number (bucket position) in constant time. That's why lookup is **O(1)** — you never scan through everything!

### Pseudo Code

```
// Creating a hash map
user = {
    "name": "Alice",
    "age": 28,
    "email": "alice@example.com"
}

// Access by key — INSTANT O(1)
name = user["name"]                    // "Alice"

// Safe access with default value
phone = GET(user, "phone", default="N/A")  // "N/A" — no crash!

// Add/Update — INSTANT O(1)
user["phone"] = "+1234567890"

// Check if key exists — INSTANT O(1)
IF "email" IN user:
    PRINT("Has email!")

// Loop through items
FOR EACH key, value IN user:
    PRINT(key + ": " + value)

// 🔥 Real-world example: Counting word frequency
text = "the cat sat on the mat the cat"
word_count = {}
FOR EACH word IN SPLIT(text, " "):
    IF word IN word_count:
        word_count[word] = word_count[word] + 1
    ELSE:
        word_count[word] = 1
// Result: {"the": 3, "cat": 2, "sat": 1, "on": 1, "mat": 1}
```

### ✅ Use Hash Maps When:
- You need **instant lookup** by a key
- You're mapping relationships (user_id → user_data)
- You're **counting** or **grouping** things
- Example: caching, configuration, JSON-like data

### ❌ Don't Use Hash Maps When:
- You need **ordered ranking** (use a sorted list or heap)
- Keys are sequential integers (just use a list)

---

## 3️⃣ Stack — The Pile of Books

### 🎯 Real-World Analogy
> A **stack of plates** in a cafeteria. You can only add or remove from the **top**. Last plate placed = first plate taken. **LIFO: Last In, First Out.**

### 📊 Visual

```mermaid
graph TD
    subgraph "📚 Stack - LIFO"
        TOP["⬆️ TOP"] --> A["📄 Page 3 - newest"]
        A --> B["📄 Page 2"]
        B --> C["📄 Page 1 - oldest"]
    end

    PUSH["push - Add to TOP"] -.-> TOP
    POP["pop - Remove from TOP"] -.-> TOP

    style TOP fill:#e74c3c,stroke:#333,color:#fff
    style A fill:#9b59b6,stroke:#333,color:#fff
    style B fill:#9b59b6,stroke:#333,color:#fff
    style C fill:#9b59b6,stroke:#333,color:#fff
    style PUSH fill:#2ecc71,stroke:#333,color:#fff
    style POP fill:#e67e22,stroke:#333,color:#fff
```

### Pseudo Code

```
stack = EMPTY_STACK

// Push (add to top)
PUSH(stack, "page_1")
PUSH(stack, "page_2")
PUSH(stack, "page_3")
// Stack: ["page_1", "page_2", "page_3"]  ← top

// Pop (remove from top)
top = POP(stack)             // "page_3"
// Stack: ["page_1", "page_2"]

// Peek (look at top without removing)
top = PEEK(stack)            // "page_2"

// 🔥 Real-world example: Undo/Redo system
CLASS TextEditor:
    text = ""
    undo_stack = EMPTY_STACK

    FUNCTION type(new_text):
        PUSH(undo_stack, text)       // Save current state
        text = text + new_text

    FUNCTION undo():
        IF NOT IS_EMPTY(undo_stack):
            text = POP(undo_stack)   // Restore previous state

editor = NEW TextEditor()
editor.type("Hello ")          // text: "Hello "
editor.type("World!")          // text: "Hello World!"
editor.undo()                  // text: "Hello "  ← magic!
```

### ✅ Use Stacks When:
- **Undo/Redo** functionality
- **Browser back button** (history of pages)
- **Parsing expressions** (matching parentheses)
- **DFS** (Depth-First Search) in graphs

---

## 4️⃣ Queue — The Movie Ticket Line

### 🎯 Real-World Analogy
> A **line at a movie theater**. First person in line = first person served. **FIFO: First In, First Out.**

### 📊 Visual

```mermaid
graph LR
    ENQ["enqueue D<br/>Join the back"] -.-> BACK

    subgraph "🎟️ Queue - FIFO"
        FRONT["🚪 FRONT"] --- A["🧑 A - first"]
        A --- B["🧑 B"]
        B --- C["🧑 C - last"]
        C --- BACK["🚪 BACK"]
    end

    FRONT -.-> DEQ["dequeue<br/>Serve from front"]

    style FRONT fill:#2ecc71,stroke:#333,color:#fff
    style BACK fill:#e74c3c,stroke:#333,color:#fff
    style A fill:#4d96ff,stroke:#333,color:#fff
    style B fill:#4d96ff,stroke:#333,color:#fff
    style C fill:#4d96ff,stroke:#333,color:#fff
```

### Pseudo Code

```
queue = EMPTY_QUEUE

// Enqueue (add to back)
ENQUEUE(queue, "customer_1")
ENQUEUE(queue, "customer_2")
ENQUEUE(queue, "customer_3")

// Dequeue (remove from front) — O(1)!
first = DEQUEUE(queue)       // "customer_1"

// ⚠️ Important: use a proper queue structure, not a list
// Removing from the front of a list is O(n) — it shifts everything!
// A proper queue (deque/linked list) does it in O(1)

// 🔥 Real-world example: Task processing queue
task_queue = EMPTY_QUEUE
ENQUEUE(task_queue, {type: "send_email", to: "alice@mail.com"})
ENQUEUE(task_queue, {type: "resize_image", file: "photo.jpg"})
ENQUEUE(task_queue, {type: "send_email", to: "bob@mail.com"})

WHILE NOT IS_EMPTY(task_queue):
    task = DEQUEUE(task_queue)
    PROCESS(task)
// Processes in order: send_email → resize_image → send_email
```

### ✅ Use Queues When:
- **Task scheduling** (process jobs in order)
- **BFS** (Breadth-First Search) in graphs
- **Message queues** in backend systems (RabbitMQ, Kafka)
- **Print queue** (documents print in order submitted)

---

## 5️⃣ Trees — The Family Tree

### 🎯 Real-World Analogy
> A **company org chart**. CEO at the top, managers below, employees below them. Each person has one boss (parent) and can manage multiple people (children).

### 📊 Binary Search Tree (BST) Visual

```mermaid
graph TD
    A["🔵 8"] --> B["🟢 3"]
    A --> C["🟢 10"]
    B --> D["🟡 1"]
    B --> E["🟡 6"]
    C --> F["🟡 14"]
    E --> G["🟠 4"]
    E --> H["🟠 7"]

    style A fill:#3498db,stroke:#333,color:#fff,stroke-width:3px
    style B fill:#2ecc71,stroke:#333,color:#fff
    style C fill:#2ecc71,stroke:#333,color:#fff
    style D fill:#f1c40f,stroke:#333,color:#333
    style E fill:#f1c40f,stroke:#333,color:#333
    style F fill:#f1c40f,stroke:#333,color:#333
    style G fill:#e67e22,stroke:#333,color:#fff
    style H fill:#e67e22,stroke:#333,color:#fff
```

> **The BST rule**: Everything to the **left** is smaller. Everything to the **right** is bigger. This means searching is like a **guessing game** — you eliminate half the tree each step! That's **O(log n)**.

### 📊 How Search Works (Finding 7)

```mermaid
graph TD
    A["8<br/>7 < 8 go LEFT"] -->|LEFT| B["3<br/>7 > 3 go RIGHT"]
    A -->|RIGHT| C["10"]
    B -->|LEFT| D["1"]
    B -->|RIGHT| E["6<br/>7 > 6 go RIGHT"]
    C -->|RIGHT| F["14"]
    E -->|LEFT| G["4"]
    E -->|RIGHT| H["✅ 7 FOUND!"]

    style A fill:#e74c3c,stroke:#333,color:#fff,stroke-width:3px
    style B fill:#e74c3c,stroke:#333,color:#fff,stroke-width:3px
    style E fill:#e74c3c,stroke:#333,color:#fff,stroke-width:3px
    style H fill:#2ecc71,stroke:#333,color:#fff,stroke-width:3px
    style C fill:#95a5a6,stroke:#333,color:#fff
    style D fill:#95a5a6,stroke:#333,color:#fff
    style F fill:#95a5a6,stroke:#333,color:#fff
    style G fill:#95a5a6,stroke:#333,color:#fff
```

> Only visited **3 nodes** out of 8 to find 7. In a list, you'd check up to **all 8**!

### Pseudo Code

```
FUNCTION bst_search(node, target):
    IF node IS NULL:
        RETURN "Not found"
    IF target == node.value:
        RETURN node
    ELSE IF target < node.value:
        RETURN bst_search(node.left, target)    // Go left (smaller side)
    ELSE:
        RETURN bst_search(node.right, target)   // Go right (bigger side)
```

### ✅ Use Trees When:
- **Hierarchical data** (file system, org chart, HTML DOM)
- **Fast search** on sorted data (BST → O(log n))
- **Databases** use B-Trees for indexing
- **Autocomplete** features (Trie — a special tree)

---

## 6️⃣ Heap — The Priority System

### 🎯 Real-World Analogy
> A **hospital emergency room**. Patients aren't served first-come-first-served — the most **critical patient** is always treated first, regardless of arrival time.

### 📊 Min-Heap Visual (smallest on top)

```mermaid
graph TD
    A["🔴 1 - highest priority"] --> B["🟠 3"]
    A --> C["🟠 2"]
    B --> D["🟡 7"]
    B --> E["🟡 6"]
    C --> F["🟡 5"]
    C --> G["🟡 4"]

    style A fill:#e74c3c,stroke:#333,color:#fff,stroke-width:3px
    style B fill:#e67e22,stroke:#333,color:#fff
    style C fill:#e67e22,stroke:#333,color:#fff
    style D fill:#f1c40f,stroke:#333,color:#333
    style E fill:#f1c40f,stroke:#333,color:#333
    style F fill:#f1c40f,stroke:#333,color:#333
    style G fill:#f1c40f,stroke:#333,color:#333
```

### Pseudo Code

```
heap = EMPTY_MIN_HEAP

// Insert — O(log n) each
HEAP_INSERT(heap, (priority=3, task="low priority task"))
HEAP_INSERT(heap, (priority=1, task="🔥 URGENT task"))
HEAP_INSERT(heap, (priority=2, task="medium priority task"))

// Extract always gives the SMALLEST (highest priority)
HEAP_EXTRACT_MIN(heap)  // (1, "🔥 URGENT task")
HEAP_EXTRACT_MIN(heap)  // (2, "medium priority task")
HEAP_EXTRACT_MIN(heap)  // (3, "low priority task")

// 🔥 Real-world example: Find the 3 cheapest products
products = [99, 15, 42, 7, 83, 23, 56, 3, 67]
top_3_cheapest = HEAP_EXTRACT_N_SMALLEST(products, 3)  // [3, 7, 15]
```

### ✅ Use Heaps When:
- **Priority queues** (task scheduling by priority)
- Finding **top K** or **bottom K** elements
- **Dijkstra's algorithm** (shortest path)
- **Merge K sorted lists**

---

## 7️⃣ Sets — The Unique Collection

### 🎯 Real-World Analogy
> A **guest list** at an exclusive party. Each name appears **only once**. Checking if someone is on the list is **instant** (like a hash map but with just keys, no values).

### Pseudo Code

```
// Remove duplicates instantly
numbers = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
unique = TO_SET(numbers)           // {1, 2, 3, 4}

// Lightning-fast membership check — O(1)
allowed = SET("alice", "bob", "charlie")
IS_IN(allowed, "alice")            // True  — O(1)
IS_IN(allowed, "dave")             // False — O(1)

// Set operations
team_a = SET("alice", "bob", "charlie")
team_b = SET("bob", "charlie", "dave")

INTERSECTION(team_a, team_b)       // {"bob", "charlie"} — in BOTH
UNION(team_a, team_b)              // {"alice", "bob", "charlie", "dave"} — in EITHER
DIFFERENCE(team_a, team_b)         // {"alice"} — only in team_a
```

### ✅ Use Sets When:
- You need **fast membership checking** — O(1) instead of O(n)
- You need to **remove duplicates**
- You need **set operations** (intersection, union, difference)
- Example: tracking seen items, filtering unique visitors

---

## 🧭 The Decision Flowchart — Which Data Structure Should I Use?

```mermaid
graph TD
    START["🤔 What do I need?"] --> Q1{"Need key-value<br/>mapping?"}
    Q1 -->|Yes| DICT["🗂️ Use Hash Map"]
    Q1 -->|No| Q2{"Need ordering<br/>or ranking?"}

    Q2 -->|Yes| Q3{"Need only<br/>min/max fast?"}
    Q3 -->|Yes| HEAP["⛰️ Use Heap"]
    Q3 -->|No| Q4{"Need sorted<br/>search?"}
    Q4 -->|Yes| TREE["🌳 Use Tree / Sorted List"]
    Q4 -->|No| LIST["📋 Use List"]

    Q2 -->|No| Q5{"LIFO?<br/>last in first out"}
    Q5 -->|Yes| STACK["📚 Use Stack"]
    Q5 -->|No| Q6{"FIFO?<br/>first in first out"}
    Q6 -->|Yes| QUEUE["🎟️ Use Queue"]
    Q6 -->|No| Q7{"Need fast<br/>membership check?"}
    Q7 -->|Yes| SET["🔵 Use Set"]
    Q7 -->|No| LIST2["📋 Use List"]

    style START fill:#e74c3c,stroke:#333,color:#fff,stroke-width:3px
    style DICT fill:#6bcb77,stroke:#333,color:#fff
    style HEAP fill:#6bcb77,stroke:#333,color:#fff
    style TREE fill:#6bcb77,stroke:#333,color:#fff
    style LIST fill:#6bcb77,stroke:#333,color:#fff
    style STACK fill:#6bcb77,stroke:#333,color:#fff
    style QUEUE fill:#6bcb77,stroke:#333,color:#fff
    style SET fill:#6bcb77,stroke:#333,color:#fff
    style LIST2 fill:#6bcb77,stroke:#333,color:#fff
```

---

## ⚡ Speed Comparison — Big-O at a Glance

| Operation | List | Hash Map | Set | Stack | Queue (Deque) | Heap |
|-----------|------|----------|-----|-------|---------------|------|
| **Access by index** | ✅ O(1) | ❌ N/A | ❌ N/A | ✅ O(1) top | ❌ N/A | ❌ N/A |
| **Search by value** | 🐌 O(n) | ✅ O(1) | ✅ O(1) | 🐌 O(n) | 🐌 O(n) | 🐌 O(n) |
| **Insert at end** | ✅ O(1) | ✅ O(1) | ✅ O(1) | ✅ O(1) | ✅ O(1) | ⚡ O(log n) |
| **Insert at start** | 🐌 O(n) | ✅ O(1) | ✅ O(1) | ❌ N/A | ✅ O(1) | ❌ N/A |
| **Delete** | 🐌 O(n) | ✅ O(1) | ✅ O(1) | ✅ O(1) top | ✅ O(1) front | ⚡ O(log n) |
| **Get min/max** | 🐌 O(n) | 🐌 O(n) | 🐌 O(n) | 🐌 O(n) | 🐌 O(n) | ✅ O(1) |

> **Rule of thumb**: If you see yourself doing `IF x IN my_list` inside a loop, you probably need a **set** or **hash map** instead. That single change can turn an O(n²) algorithm into O(n)!

---

## 🏋️ Practice Exercises

### Exercise 1: Two Sum (Easy)
> Given a list of numbers and a target, find two numbers that add up to the target. Return their indices.
> **Hint**: Which data structure gives you O(1) lookup?
```
// Input:  nums = [2, 7, 11, 15], target = 9
// Output: [0, 1]  because nums[0] + nums[1] = 2 + 7 = 9
```

### Exercise 2: Valid Parentheses (Easy)
> Given a string of brackets `()[]{}`, check if they're properly matched.
> **Hint**: Which data structure follows LIFO?
```
// Input:  "({[]})"  → True
// Input:  "({[}])"  → False
```

### Exercise 3: Recent Calls Counter (Easy)
> Count how many requests happened in the last 3000 milliseconds.
> **Hint**: Which data structure follows FIFO?

### Exercise 4: Top K Frequent Words (Medium)
> Given a list of words, return the K most frequent ones.
> **Hint**: Combine a hash map with a heap.

### Exercise 5: LRU Cache (Hard)
> Design a cache that evicts the least recently used item when full.
> **Hint**: Combine a hash map with a doubly-linked list.

---

## 🎤 Interview Corner

> **Q: "When would you choose a hash map over a list?"**
>
> **Great answer**: "When I need O(1) lookups by a key instead of scanning through the entire collection. For example, if I'm building a user session store, I'd use `{session_id: user_data}` so I can instantly find any user's session without iterating."

> **Q: "What's the difference between a stack and a queue?"**
>
> **Great answer**: "A stack is LIFO — like the browser back button, the last page you visited is the first you go back to. A queue is FIFO — like a print queue, the first document submitted prints first. I use stacks for DFS and undo systems, queues for BFS and task processing."

> **Q: "Why not just use lists for everything?"**
>
> **Great answer**: "Lists are O(n) for search and membership checks. If I'm checking `if user_id in users_list` inside a loop of 10,000 items, that's O(n²) = 100 million operations. Switching to a set makes it O(n) = 10,000 operations. Choosing the right data structure is often the easiest performance win."

---

## ✅ Key Takeaway

> **The fastest way to speed up your code isn't clever algorithms — it's picking the right data structure.** A hash map/set lookup is **1000x faster** than scanning a list when you have 1000 items.

---

**Next up → [Topic 1.2: Algorithm Thinking & Big-O Notation](../1.2-Algorithms-BigO/)**
