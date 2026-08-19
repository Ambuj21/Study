"""
Topic 1.4 - Database Fundamentals: Python Implementation
Demonstrates SQL operations using SQLite (built into Python, no install needed).

Usage:
    python code.py
"""
import sqlite3
import os
import time


# ================================================================
# SETUP: Create an in-memory database
# ================================================================

# SQLite is built into Python — no installation needed!
# Using :memory: creates a temporary database in RAM
db = sqlite3.connect(":memory:")
db.row_factory = sqlite3.Row  # Access columns by name
cursor = db.cursor()

print("=" * 60)
print("  DATABASE FUNDAMENTALS - Live Demo with SQLite")
print("=" * 60)


# ================================================================
# 1. CREATE TABLES — Schema Design
# ================================================================

print("\n" + "=" * 60)
print("  1. CREATING TABLES (Schema Design)")
print("=" * 60)

cursor.executescript("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        city TEXT,
        age INTEGER CHECK(age > 0),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT,
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'published')),
        published_at TIMESTAMP,
        FOREIGN KEY (author_id) REFERENCES users(id)
    );

    CREATE TABLE comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        body TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE post_tags (
        post_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (post_id, tag_id),
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (tag_id) REFERENCES tags(id)
    );
""")

print("  Tables created: users, posts, comments, tags, post_tags")

# Verify tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row["name"] for row in cursor.fetchall()]
print(f"  Tables in database: {tables}")


# ================================================================
# 2. INSERT DATA — CRUD: Create
# ================================================================

print("\n" + "=" * 60)
print("  2. INSERTING DATA (CRUD: Create)")
print("=" * 60)

# Insert users
users_data = [
    ("Alice", "alice@mail.com", "New York", 28),
    ("Bob", "bob@mail.com", "London", 34),
    ("Charlie", "charlie@mail.com", "New York", 22),
    ("Diana", "diana@mail.com", "Paris", 31),
    ("Eve", "eve@mail.com", "London", 27),
]

cursor.executemany(
    "INSERT INTO users (name, email, city, age) VALUES (?, ?, ?, ?)",
    users_data
)

# Insert posts
posts_data = [
    (1, "Getting Started with SQL", "Learn the basics...", "published", "2024-01-15"),
    (1, "Advanced Joins", "Deep dive into joins...", "published", "2024-02-20"),
    (2, "Python for Beginners", "Start coding today...", "published", "2024-03-10"),
    (2, "My Draft Post", "Work in progress...", "draft", None),
    (3, "Database Indexing", "Speed up your queries...", "published", "2024-04-05"),
]

cursor.executemany(
    "INSERT INTO posts (author_id, title, content, status, published_at) VALUES (?, ?, ?, ?, ?)",
    posts_data
)

# Insert comments
comments_data = [
    (1, 2, "Great article!"),
    (1, 3, "Very helpful, thanks!"),
    (2, 1, "Nice explanation"),
    (3, 1, "Learned a lot"),
    (5, 3, "Clear and concise"),
]

cursor.executemany(
    "INSERT INTO comments (post_id, user_id, body) VALUES (?, ?, ?)",
    comments_data
)

# Insert tags
tags_data = [("SQL",), ("Python",), ("Database",), ("Tutorial",)]
cursor.executemany("INSERT INTO tags (name) VALUES (?)", tags_data)

# Link posts to tags
post_tags_data = [(1, 1), (1, 3), (1, 4), (2, 1), (3, 2), (3, 4), (5, 3)]
cursor.executemany("INSERT INTO post_tags (post_id, tag_id) VALUES (?, ?)", post_tags_data)

db.commit()
print(f"  Inserted {len(users_data)} users")
print(f"  Inserted {len(posts_data)} posts")
print(f"  Inserted {len(comments_data)} comments")
print(f"  Inserted {len(tags_data)} tags")


# ================================================================
# 3. SELECT QUERIES — CRUD: Read
# ================================================================

print("\n" + "=" * 60)
print("  3. SELECT QUERIES (CRUD: Read)")
print("=" * 60)

# Simple SELECT
print("\n  --- All users from New York ---")
cursor.execute("SELECT name, email, age FROM users WHERE city = 'New York'")
for row in cursor.fetchall():
    print(f"    {row['name']} | {row['email']} | age: {row['age']}")

# SELECT with ORDER BY and LIMIT
print("\n  --- Top 3 oldest users ---")
cursor.execute("SELECT name, age FROM users ORDER BY age DESC LIMIT 3")
for row in cursor.fetchall():
    print(f"    {row['name']}: {row['age']} years old")


# ================================================================
# 4. JOINS — Connecting Tables
# ================================================================

print("\n" + "=" * 60)
print("  4. JOINS (Connecting Tables)")
print("=" * 60)

# INNER JOIN — Users with their posts
print("\n  --- INNER JOIN: Users + Posts ---")
cursor.execute("""
    SELECT users.name, posts.title, posts.status
    FROM users
    INNER JOIN posts ON users.id = posts.author_id
    ORDER BY users.name
""")
for row in cursor.fetchall():
    print(f"    {row['name']:10s} | {row['title']:30s} | {row['status']}")

# LEFT JOIN — All users, even without posts
print("\n  --- LEFT JOIN: ALL users (even without posts) ---")
cursor.execute("""
    SELECT users.name, COUNT(posts.id) AS post_count
    FROM users
    LEFT JOIN posts ON users.id = posts.author_id
    GROUP BY users.id
    ORDER BY post_count DESC
""")
for row in cursor.fetchall():
    posts = row['post_count']
    indicator = " (no posts)" if posts == 0 else ""
    print(f"    {row['name']:10s} | {posts} posts{indicator}")

# Multi-table JOIN — Posts with author names and comment counts
print("\n  --- Multi-JOIN: Posts + Authors + Comment Count ---")
cursor.execute("""
    SELECT
        posts.title,
        users.name AS author,
        COUNT(comments.id) AS comment_count
    FROM posts
    INNER JOIN users ON posts.author_id = users.id
    LEFT JOIN comments ON posts.id = comments.post_id
    WHERE posts.status = 'published'
    GROUP BY posts.id
    ORDER BY comment_count DESC
""")
for row in cursor.fetchall():
    print(f"    {row['title']:30s} | by {row['author']:8s} | {row['comment_count']} comments")


# ================================================================
# 5. AGGREGATION — Counting, Summing, Grouping
# ================================================================

print("\n" + "=" * 60)
print("  5. AGGREGATION (COUNT, SUM, AVG, GROUP BY)")
print("=" * 60)

# Posts per status
print("\n  --- Posts by status ---")
cursor.execute("""
    SELECT status, COUNT(*) AS total
    FROM posts
    GROUP BY status
""")
for row in cursor.fetchall():
    print(f"    {row['status']:12s} | {row['total']} posts")

# Average age by city
print("\n  --- Average age by city ---")
cursor.execute("""
    SELECT city, ROUND(AVG(age), 1) AS avg_age, COUNT(*) AS user_count
    FROM users
    GROUP BY city
    ORDER BY avg_age DESC
""")
for row in cursor.fetchall():
    print(f"    {row['city']:12s} | avg age: {row['avg_age']} | {row['user_count']} users")

# HAVING — filter on aggregated results
print("\n  --- Cities with more than 1 user (using HAVING) ---")
cursor.execute("""
    SELECT city, COUNT(*) AS user_count
    FROM users
    GROUP BY city
    HAVING user_count > 1
""")
for row in cursor.fetchall():
    print(f"    {row['city']}: {row['user_count']} users")


# ================================================================
# 6. SUBQUERIES
# ================================================================

print("\n" + "=" * 60)
print("  6. SUBQUERIES (Query inside a query)")
print("=" * 60)

# Users who have published posts
print("\n  --- Users who have published at least one post ---")
cursor.execute("""
    SELECT name FROM users
    WHERE id IN (
        SELECT DISTINCT author_id FROM posts WHERE status = 'published'
    )
""")
for row in cursor.fetchall():
    print(f"    {row['name']}")

# Users who have NEVER posted
print("\n  --- Users who have NEVER posted ---")
cursor.execute("""
    SELECT name FROM users
    WHERE id NOT IN (
        SELECT DISTINCT author_id FROM posts
    )
""")
for row in cursor.fetchall():
    print(f"    {row['name']} (no posts!)")


# ================================================================
# 7. TRANSACTIONS — ACID in Action
# ================================================================

print("\n" + "=" * 60)
print("  7. TRANSACTIONS (ACID in Action)")
print("=" * 60)

# Simulate a bank transfer with ACID guarantees
cursor.executescript("""
    CREATE TABLE accounts (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        balance REAL NOT NULL CHECK(balance >= 0)
    );
    INSERT INTO accounts VALUES (1, 'Alice', 1000.00);
    INSERT INTO accounts VALUES (2, 'Bob', 500.00);
""")

print("\n  --- Before transfer ---")
cursor.execute("SELECT name, balance FROM accounts")
for row in cursor.fetchall():
    print(f"    {row['name']}: ${row['balance']:.2f}")


def transfer_money(db, from_id, to_id, amount):
    """Transfer money with ACID transaction."""
    try:
        cursor = db.cursor()

        # Check balance first
        cursor.execute("SELECT balance FROM accounts WHERE id = ?", (from_id,))
        balance = cursor.fetchone()["balance"]

        if balance < amount:
            print(f"    Transfer FAILED: Insufficient funds (has ${balance}, needs ${amount})")
            return False

        # Perform transfer (both operations in one transaction)
        cursor.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?",
            (amount, from_id)
        )
        cursor.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (amount, to_id)
        )

        db.commit()  # COMMIT = save both changes permanently
        print(f"    Transfer of ${amount:.2f} successful!")
        return True

    except Exception as e:
        db.rollback()  # ROLLBACK = undo ALL changes if anything fails
        print(f"    Transfer FAILED and ROLLED BACK: {e}")
        return False


# Successful transfer
print("\n  --- Transferring $200 from Alice to Bob ---")
transfer_money(db, 1, 2, 200)

print("\n  --- After transfer ---")
cursor.execute("SELECT name, balance FROM accounts")
for row in cursor.fetchall():
    print(f"    {row['name']}: ${row['balance']:.2f}")

# Failed transfer (insufficient funds)
print("\n  --- Attempting to transfer $5000 from Alice (only has $800) ---")
transfer_money(db, 1, 2, 5000)

print("\n  --- Balances unchanged after failed transfer ---")
cursor.execute("SELECT name, balance FROM accounts")
for row in cursor.fetchall():
    print(f"    {row['name']}: ${row['balance']:.2f}")


# ================================================================
# 8. INDEXING — Performance Demo
# ================================================================

print("\n" + "=" * 60)
print("  8. INDEXING (Performance Comparison)")
print("=" * 60)

# Create a large table for testing
cursor.execute("""
    CREATE TABLE large_users (
        id INTEGER PRIMARY KEY,
        email TEXT,
        name TEXT,
        score INTEGER
    )
""")

# Insert 100,000 rows
print("\n  Inserting 100,000 rows...")
data = [(f"user{i}@mail.com", f"User {i}", i % 100) for i in range(100_000)]
cursor.executemany(
    "INSERT INTO large_users (email, name, score) VALUES (?, ?, ?)",
    data
)
db.commit()
print("  Done!")

# Query WITHOUT index
print("\n  --- Query WITHOUT index ---")
start = time.perf_counter()
for _ in range(100):
    cursor.execute(
        "SELECT * FROM large_users WHERE email = 'user99999@mail.com'"
    )
    cursor.fetchone()
no_index_time = time.perf_counter() - start
print(f"    100 lookups took: {no_index_time:.4f}s")

# Create index
print("\n  Creating index on email column...")
cursor.execute("CREATE INDEX idx_email ON large_users(email)")
db.commit()
print("  Index created!")

# Query WITH index
print("\n  --- Query WITH index ---")
start = time.perf_counter()
for _ in range(100):
    cursor.execute(
        "SELECT * FROM large_users WHERE email = 'user99999@mail.com'"
    )
    cursor.fetchone()
with_index_time = time.perf_counter() - start
print(f"    100 lookups took: {with_index_time:.4f}s")

speedup = no_index_time / with_index_time if with_index_time > 0 else 0
print(f"\n    Index made queries {speedup:.1f}x faster!")


# ================================================================
# 9. EXPLAIN — See How the Database Thinks
# ================================================================

print("\n" + "=" * 60)
print("  9. EXPLAIN QUERY PLAN (How the DB executes your query)")
print("=" * 60)

print("\n  --- Without index (score column) ---")
cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM large_users WHERE score = 50")
for row in cursor.fetchall():
    print(f"    {row['detail']}")

print("\n  --- With index (email column) ---")
cursor.execute(
    "EXPLAIN QUERY PLAN SELECT * FROM large_users WHERE email = 'user500@mail.com'"
)
for row in cursor.fetchall():
    print(f"    {row['detail']}")

print("\n  (SCAN = slow full table scan, SEARCH = fast index lookup)")


# ================================================================
# CLEANUP
# ================================================================

db.close()

print("\n" + "=" * 60)
print("  Topic 1.4 Complete!")
print("  Say 'next' for Topic 1.5: Python Deep Dive")
print("=" * 60)
