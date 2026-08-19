"""
Topic 1.5 - Python Deep Dive: Runnable Code Examples
Demonstrates OOP, decorators, generators, context managers, type hints,
dunder methods, dataclasses, and error handling.

Usage:
    python code.py
"""
import time
import functools
from dataclasses import dataclass, field
from typing import Optional


# ================================================================
# 1. OOP — Classes, Inheritance, Polymorphism
# ================================================================

print("=" * 60)
print("  1. OOP — Classes, Inheritance, Polymorphism")
print("=" * 60)


class Animal:
    """Base class for all animals."""

    def __init__(self, name: str, sound: str):
        self.name = name
        self.sound = sound

    def speak(self) -> str:
        return f"{self.name} says {self.sound}!"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


class Dog(Animal):
    """Dog inherits from Animal and adds fetch behavior."""

    def __init__(self, name: str, breed: str):
        super().__init__(name, "Woof")  # Call parent constructor
        self.breed = breed

    def fetch(self, item: str) -> str:
        return f"{self.name} fetches the {item}!"


class Cat(Animal):
    """Cat inherits from Animal and overrides speak (polymorphism)."""

    def __init__(self, name: str, indoor: bool = True):
        super().__init__(name, "Meow")
        self.indoor = indoor

    def speak(self) -> str:  # OVERRIDE parent's method
        if self.indoor:
            return f"{self.name} softly purrs..."
        return super().speak()  # Use parent's version


# Polymorphism in action — same method, different behavior
animals = [Dog("Rex", "Labrador"), Cat("Whiskers", indoor=True), Dog("Buddy", "Poodle")]

print("\n  Polymorphism demo:")
for animal in animals:
    print(f"    {animal} -> {animal.speak()}")

print(f"\n  Dog-specific: {animals[0].fetch('ball')}")

# Encapsulation — private attributes
print("\n  Encapsulation demo:")


class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner
        self._balance = balance  # _ = convention for "private"

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self._balance += amount

    def get_balance(self) -> float:
        return self._balance  # Controlled access


account = BankAccount("Alice", 1000)
account.deposit(500)
print(f"    Alice's balance: ${account.get_balance()}")
# account._balance = 0  # You CAN do this, but you SHOULDN'T (convention)


# ================================================================
# 2. DECORATORS — Functions That Modify Functions
# ================================================================

print("\n" + "=" * 60)
print("  2. DECORATORS")
print("=" * 60)


# --- Timer decorator ---
def timer(func):
    """Measure execution time of a function."""
    @functools.wraps(func)  # Preserves original function's name/docstring
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"    @timer: {func.__name__} took {elapsed:.6f}s")
        return result
    return wrapper


# --- Logger decorator ---
def logger(func):
    """Log function calls with arguments."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_str = ", ".join([str(a) for a in args])
        print(f"    @logger: Calling {func.__name__}({args_str})")
        result = func(*args, **kwargs)
        print(f"    @logger: {func.__name__} returned {result}")
        return result
    return wrapper


# --- Retry decorator (with arguments!) ---
def retry(max_attempts: int = 3, delay: float = 0.1):
    """Retry a function up to max_attempts times."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"    @retry: Attempt {attempt}/{max_attempts} failed: {e}")
                    if attempt == max_attempts:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator


# --- Cache decorator (memoization) ---
def cache(func):
    """Cache function results (simple memoization)."""
    memo = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args not in memo:
            memo[args] = func(*args)
            print(f"    @cache: Computed {func.__name__}{args}")
        else:
            print(f"    @cache: Cache HIT for {func.__name__}{args}")
        return memo[args]
    return wrapper


# Using decorators
@timer
@logger
def slow_add(a: int, b: int) -> int:
    """Add two numbers (pretend it's slow)."""
    time.sleep(0.01)
    return a + b


print("\n  --- Timer + Logger decorators ---")
result = slow_add(3, 7)

print("\n  --- Cache decorator ---")


@cache
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


fib_10 = fibonacci(10)
print(f"    fibonacci(10) = {fib_10}")
print("    (Notice: each value computed only ONCE thanks to caching)")

print("\n  --- Retry decorator ---")
attempt_count = 0


@retry(max_attempts=3, delay=0.05)
def flaky_function():
    global attempt_count
    attempt_count += 1
    if attempt_count < 3:
        raise ConnectionError("Server unavailable")
    return "Success!"


try:
    result = flaky_function()
    print(f"    Final result: {result}")
except ConnectionError:
    print("    All retries exhausted")


# ================================================================
# 3. GENERATORS — Lazy Data Streams
# ================================================================

print("\n" + "=" * 60)
print("  3. GENERATORS — Lazy Data Streams")
print("=" * 60)

import sys


# Regular list vs generator — memory comparison
big_list = [x * x for x in range(100_000)]    # List
big_gen = (x * x for x in range(100_000))     # Generator

print(f"\n  List memory:      {sys.getsizeof(big_list):>10,} bytes")
print(f"  Generator memory: {sys.getsizeof(big_gen):>10,} bytes")
print(f"  List uses {sys.getsizeof(big_list) / sys.getsizeof(big_gen):.0f}x more memory!")


# Generator function with yield
def fibonacci_gen(limit: int):
    """Generate Fibonacci numbers up to limit."""
    a, b = 0, 1
    while a < limit:
        yield a        # Pause here, return value, resume on next call
        a, b = b, a + b


print("\n  Fibonacci numbers < 100:")
print(f"    {list(fibonacci_gen(100))}")


# Generator pipeline — chaining generators
def read_lines(text: str):
    """Simulate reading lines from a file."""
    for line in text.split("\n"):
        yield line


def filter_errors(lines):
    """Only yield lines containing ERROR."""
    for line in lines:
        if "ERROR" in line:
            yield line


def extract_message(lines):
    """Extract the message part after the level."""
    for line in lines:
        parts = line.split("] ")
        if len(parts) > 1:
            yield parts[-1]


# Pipeline: read -> filter -> extract
log_data = """[INFO] Server started
[ERROR] Database connection failed
[INFO] Processing request
[ERROR] Timeout on API call
[INFO] Request completed
[ERROR] Disk space low"""

print("\n  Generator pipeline (log processing):")
pipeline = extract_message(filter_errors(read_lines(log_data)))
for error in pipeline:
    print(f"    Found: {error}")


# ================================================================
# 4. CONTEXT MANAGERS — Clean Resource Handling
# ================================================================

print("\n" + "=" * 60)
print("  4. CONTEXT MANAGERS")
print("=" * 60)


# Custom context manager using a class
class Timer:
    """Context manager that times a block of code."""

    def __init__(self, label: str = "Block"):
        self.label = label

    def __enter__(self):
        self.start = time.perf_counter()
        print(f"    [{self.label}] Started...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start
        print(f"    [{self.label}] Finished in {self.elapsed:.6f}s")
        return False  # Don't suppress exceptions


print("\n  --- Timer context manager ---")
with Timer("sorting"):
    data = [i for i in range(100_000, 0, -1)]
    data.sort()

with Timer("list comprehension"):
    squares = [x ** 2 for x in range(100_000)]


# Context manager using contextlib (simpler syntax)
from contextlib import contextmanager


@contextmanager
def temporary_value(obj, attr, new_value):
    """Temporarily change an attribute, restore after block."""
    old_value = getattr(obj, attr)
    setattr(obj, attr, new_value)
    print(f"    Changed {attr}: {old_value} -> {new_value}")
    try:
        yield obj
    finally:
        setattr(obj, attr, old_value)
        print(f"    Restored {attr}: {new_value} -> {old_value}")


class Config:
    debug = False
    log_level = "INFO"


print("\n  --- Temporary value context manager ---")
config = Config()
print(f"    Before: debug={config.debug}")
with temporary_value(config, "debug", True):
    print(f"    Inside: debug={config.debug}")
print(f"    After:  debug={config.debug}")


# ================================================================
# 5. TYPE HINTS
# ================================================================

print("\n" + "=" * 60)
print("  5. TYPE HINTS")
print("=" * 60)


def find_user(
    users: list[dict[str, str]],
    name: str
) -> Optional[dict[str, str]]:
    """Find a user by name. Returns None if not found."""
    for user in users:
        if user["name"] == name:
            return user
    return None


def process_scores(
    scores: list[int],
    min_score: int = 0
) -> dict[str, float]:
    """Calculate statistics for scores above min_score."""
    filtered = [s for s in scores if s >= min_score]
    return {
        "count": len(filtered),
        "average": sum(filtered) / len(filtered) if filtered else 0,
        "max": max(filtered) if filtered else 0,
    }


users = [{"name": "Alice", "email": "alice@mail.com"}, {"name": "Bob", "email": "bob@mail.com"}]
result = find_user(users, "Alice")
print(f"\n  find_user result: {result}")

stats = process_scores([85, 92, 78, 95, 60, 88], min_score=80)
print(f"  Score stats: {stats}")


# ================================================================
# 6. DUNDER METHODS — Custom Object Behavior
# ================================================================

print("\n" + "=" * 60)
print("  6. DUNDER METHODS — Custom Object Behavior")
print("=" * 60)


class Vector:
    """A mathematical vector with operator overloading."""

    def __init__(self, *components: float):
        self.components = list(components)

    def __repr__(self) -> str:
        return f"Vector{tuple(self.components)}"

    def __add__(self, other: "Vector") -> "Vector":
        paired = zip(self.components, other.components)
        return Vector(*(a + b for a, b in paired))

    def __sub__(self, other: "Vector") -> "Vector":
        paired = zip(self.components, other.components)
        return Vector(*(a - b for a, b in paired))

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(*(c * scalar for c in self.components))

    def __eq__(self, other: "Vector") -> bool:
        return self.components == other.components

    def __len__(self) -> int:
        return len(self.components)

    def __getitem__(self, index: int) -> float:
        return self.components[index]

    def __iter__(self):
        return iter(self.components)

    def magnitude(self) -> float:
        return sum(c ** 2 for c in self.components) ** 0.5


v1 = Vector(1, 2, 3)
v2 = Vector(4, 5, 6)

print(f"\n  v1 = {v1}")
print(f"  v2 = {v2}")
print(f"  v1 + v2 = {v1 + v2}")           # __add__
print(f"  v2 - v1 = {v2 - v1}")           # __sub__
print(f"  v1 * 3 = {v1 * 3}")             # __mul__
print(f"  v1 == v2? {v1 == v2}")           # __eq__
print(f"  len(v1) = {len(v1)}")            # __len__
print(f"  v1[0] = {v1[0]}")               # __getitem__
print(f"  magnitude of v1 = {v1.magnitude():.4f}")
print(f"  Unpack v1: ", end="")
for component in v1:                       # __iter__
    print(f"{component} ", end="")
print()


# ================================================================
# 7. DATACLASSES — Less Boilerplate
# ================================================================

print("\n" + "=" * 60)
print("  7. DATACLASSES — Auto-generated methods")
print("=" * 60)


@dataclass
class Product:
    name: str
    price: float
    quantity: int = 0
    tags: list[str] = field(default_factory=list)

    def total_value(self) -> float:
        return self.price * self.quantity

    def is_in_stock(self) -> bool:
        return self.quantity > 0


@dataclass(frozen=True)  # Immutable!
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


# Dataclass auto-generates __init__, __repr__, __eq__
laptop = Product("Laptop", 999.99, 5, ["electronics", "computers"])
mouse = Product("Mouse", 29.99, 0)

print(f"\n  {laptop}")  # Auto __repr__
print(f"  Total value: ${laptop.total_value()}")
print(f"  In stock? {laptop.is_in_stock()}")
print(f"  {mouse}")
print(f"  In stock? {mouse.is_in_stock()}")
print(f"  laptop == laptop? {laptop == Product('Laptop', 999.99, 5, ['electronics', 'computers'])}")

p1 = Point(0, 0)
p2 = Point(3, 4)
print(f"\n  Distance from {p1} to {p2}: {p1.distance_to(p2)}")

try:
    p1.x = 10  # Should fail — frozen!
except AttributeError as e:
    print(f"  Frozen dataclass: {e}")


# ================================================================
# 8. ERROR HANDLING
# ================================================================

print("\n" + "=" * 60)
print("  8. ERROR HANDLING — Custom Exceptions")
print("=" * 60)


# Custom exceptions
class InsufficientFundsError(Exception):
    def __init__(self, balance: float, amount: float):
        self.balance = balance
        self.amount = amount
        super().__init__(f"Cannot withdraw ${amount} from balance of ${balance}")


class AccountLockedError(Exception):
    pass


class SmartAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner
        self.balance = balance
        self.locked = False

    def withdraw(self, amount: float) -> float:
        if self.locked:
            raise AccountLockedError(f"{self.owner}'s account is locked")
        if amount > self.balance:
            raise InsufficientFundsError(self.balance, amount)
        self.balance -= amount
        return self.balance


acc = SmartAccount("Alice", 100)

# Test various error scenarios
test_cases = [
    ("Withdraw $50 (valid)", lambda: acc.withdraw(50)),
    ("Withdraw $200 (insufficient)", lambda: acc.withdraw(200)),
    ("Withdraw from locked account", lambda: (setattr(acc, "locked", True), acc.withdraw(10))),
]

for description, action in test_cases:
    print(f"\n  --- {description} ---")
    try:
        result = action()
        print(f"    Success! Balance: ${acc.balance}")
    except InsufficientFundsError as e:
        print(f"    InsufficientFundsError: {e}")
    except AccountLockedError as e:
        print(f"    AccountLockedError: {e}")
    except Exception as e:
        print(f"    Unexpected: {type(e).__name__}: {e}")


# ================================================================
# 9. COMPREHENSIONS
# ================================================================

print("\n" + "=" * 60)
print("  9. COMPREHENSIONS — Elegant Transformations")
print("=" * 60)

# List comprehension
numbers = list(range(1, 11))
even_squares = [n ** 2 for n in numbers if n % 2 == 0]
print(f"\n  Even squares of {numbers}:")
print(f"    {even_squares}")

# Dict comprehension
words = ["hello", "world", "python", "is", "awesome"]
word_lengths = {w: len(w) for w in words}
print(f"\n  Word lengths: {word_lengths}")

# Set comprehension
text = "the cat sat on the mat by the cat"
unique_words = {word for word in text.split()}
print(f"\n  Unique words: {unique_words}")

# Nested comprehension
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]
print(f"\n  Flattened {matrix}:")
print(f"    {flat}")

# Conditional comprehension
grades = {"Alice": 92, "Bob": 67, "Charlie": 85, "Diana": 45, "Eve": 78}
passed = {name: grade for name, grade in grades.items() if grade >= 70}
print(f"\n  Passed students: {passed}")


print("\n" + "=" * 60)
print("  Phase 1: Foundations COMPLETE!")
print("  Say 'start' to begin Phase 2: System Design")
print("=" * 60)
