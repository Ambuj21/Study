"""
📘 Topic 1.1 — Data Structures: Hands-On Practice
Run this file to see each data structure in action!

Usage: python examples.py
"""


# ═══════════════════════════════════════════════════
# 1️⃣  LISTS — The Ordered Shelf
# ═══════════════════════════════════════════════════

print("=" * 50)
print("1️⃣  LISTS — The Ordered Shelf")
print("=" * 50)

fruits = ["apple", "banana", "cherry", "date"]

# Access by index — INSTANT O(1)
print(f"Index 2: {fruits[2]}")           # cherry

# Append — FAST O(1)
fruits.append("elderberry")
print(f"After append: {fruits}")

# Insert — SLOW O(n) (shifts everything)
fruits.insert(1, "blueberry")
print(f"After insert at 1: {fruits}")

# List comprehension — transform data
prices = [10, 20, 30, 40]
discounted = [p * 0.9 for p in prices]
print(f"Discounted prices: {discounted}")

print()


# ═══════════════════════════════════════════════════
# 2️⃣  DICTIONARIES — The Filing Cabinet
# ═══════════════════════════════════════════════════

print("=" * 50)
print("2️⃣  DICTIONARIES — The Filing Cabinet")
print("=" * 50)

user = {"name": "Alice", "age": 28, "email": "alice@example.com"}

# Access by key — INSTANT O(1)
print(f"Name: {user['name']}")

# Safe access with .get()
print(f"Phone: {user.get('phone', 'N/A')}")

# Word frequency counter — classic dict use case
text = "the cat sat on the mat the cat"
word_count = {}
for word in text.split():
    word_count[word] = word_count.get(word, 0) + 1
print(f"Word counts: {word_count}")

print()


# ═══════════════════════════════════════════════════
# 3️⃣  STACKS — The Pile of Books (LIFO)
# ═══════════════════════════════════════════════════

print("=" * 50)
print("3️⃣  STACKS — LIFO (Last In, First Out)")
print("=" * 50)


class TextEditor:
    """A simple text editor with undo using a stack."""

    def __init__(self):
        self.text = ""
        self.undo_stack = []

    def type(self, new_text):
        self.undo_stack.append(self.text)
        self.text += new_text
        print(f"  Typed '{new_text}' → text: '{self.text}'")

    def undo(self):
        if self.undo_stack:
            self.text = self.undo_stack.pop()
            print(f"  Undo! → text: '{self.text}'")


editor = TextEditor()
editor.type("Hello ")
editor.type("World!")
editor.undo()    # Goes back to "Hello "
editor.undo()    # Goes back to ""

print()


# ═══════════════════════════════════════════════════
# 4️⃣  QUEUES — The Movie Ticket Line (FIFO)
# ═══════════════════════════════════════════════════

print("=" * 50)
print("4️⃣  QUEUES — FIFO (First In, First Out)")
print("=" * 50)

from collections import deque

task_queue = deque()
task_queue.append({"type": "send_email", "to": "alice@mail.com"})
task_queue.append({"type": "resize_image", "file": "photo.jpg"})
task_queue.append({"type": "send_email", "to": "bob@mail.com"})

print("Processing tasks in order:")
while task_queue:
    task = task_queue.popleft()  # O(1) — much faster than list.pop(0)!
    print(f"  ✅ {task['type']} → {list(task.values())[1]}")

print()


# ═══════════════════════════════════════════════════
# 5️⃣  SETS — The Unique Collection
# ═══════════════════════════════════════════════════

print("=" * 50)
print("5️⃣  SETS — Fast Membership Check O(1)")
print("=" * 50)

# Remove duplicates instantly
numbers = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
unique = set(numbers)
print(f"Unique numbers: {unique}")

# Lightning-fast "in" check
allowed_users = {"alice", "bob", "charlie"}
print(f"Is 'alice' allowed? {'alice' in allowed_users}")   # True — O(1)
print(f"Is 'dave' allowed? {'dave' in allowed_users}")     # False — O(1)

# Set operations
team_a = {"alice", "bob", "charlie"}
team_b = {"bob", "charlie", "dave"}
print(f"In both teams: {team_a & team_b}")        # intersection
print(f"In either team: {team_a | team_b}")        # union
print(f"Only in team A: {team_a - team_b}")        # difference

print()


# ═══════════════════════════════════════════════════
# 6️⃣  HEAPS — The Priority System
# ═══════════════════════════════════════════════════

print("=" * 50)
print("6️⃣  HEAPS — Priority Queue")
print("=" * 50)

import heapq

# Hospital ER: patients by severity (lower = more urgent)
er_queue = []
heapq.heappush(er_queue, (3, "Broken finger"))
heapq.heappush(er_queue, (1, "🔥 Heart attack"))
heapq.heappush(er_queue, (2, "Deep cut"))
heapq.heappush(er_queue, (5, "Common cold"))

print("Treating patients by priority:")
while er_queue:
    priority, patient = heapq.heappop(er_queue)
    print(f"  Priority {priority}: {patient}")

# Top K: Find 3 cheapest products
products = [99, 15, 42, 7, 83, 23, 56, 3, 67]
cheapest_3 = heapq.nsmallest(3, products)
print(f"\n3 cheapest products: {cheapest_3}")

print()


# ═══════════════════════════════════════════════════
# 🔥 BONUS: Performance Comparison
# ═══════════════════════════════════════════════════

print("=" * 50)
print("🔥 PERFORMANCE: List vs Set lookup")
print("=" * 50)

import time

size = 1_000_000
data_list = list(range(size))
data_set = set(range(size))

# Search in LIST
start = time.perf_counter()
_ = 999_999 in data_list
list_time = time.perf_counter() - start

# Search in SET
start = time.perf_counter()
_ = 999_999 in data_set
set_time = time.perf_counter() - start

print(f"List search: {list_time:.6f} seconds")
print(f"Set search:  {set_time:.6f} seconds")
print(f"Set is {list_time / set_time:.0f}x faster! 🚀")

print()
print("✅ Topic 1.1 Complete! Say 'next' for Topic 1.2: Algorithms & Big-O")
