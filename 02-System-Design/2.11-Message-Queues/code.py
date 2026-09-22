"""
System Design Topic 11 - Message Queues: Python Simulations

Demonstrates:
- Sync vs Async processing comparison
- Producer-Consumer pattern with threading
- Pub/Sub pattern (one event → multiple consumers)
- Dead Letter Queue handling
- Backpressure simulation
- Message ordering and idempotency

Usage:
    python code.py
"""
import time
import random
import threading
import queue
from dataclasses import dataclass, field
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor


# ================================================================
# 1. SYNC vs ASYNC — Speed Comparison
# ================================================================

print("=" * 60)
print("  1. SYNC vs ASYNC — Why Message Queues Exist")
print("=" * 60)


def sync_photo_upload():
    """Synchronous — user waits for everything."""
    start = time.perf_counter()

    time.sleep(0.010)  # Save to storage (10ms)
    time.sleep(0.200)  # Resize to 6 sizes (200ms)
    time.sleep(0.150)  # ML content moderation (150ms)
    time.sleep(0.050)  # Update feed for followers (50ms)
    time.sleep(0.030)  # Send push notification (30ms)

    return (time.perf_counter() - start) * 1000


def async_photo_upload(task_queue):
    """Asynchronous — user gets immediate response, work queued."""
    start = time.perf_counter()

    time.sleep(0.010)  # Save to storage (10ms)

    # Queue background tasks (instant — just adds to queue)
    task_queue.put(("resize", 0.200))
    task_queue.put(("moderation", 0.150))
    task_queue.put(("update_feed", 0.050))
    task_queue.put(("notification", 0.030))

    return (time.perf_counter() - start) * 1000


# Compare
sync_time = sync_photo_upload()

task_q = queue.Queue()
async_time = async_photo_upload(task_q)

print(f"\n  Photo Upload — User-Facing Latency:")
print(f"    Synchronous:  {sync_time:>8.0f}ms (user waits for EVERYTHING)")
print(f"    Asynchronous: {async_time:>8.0f}ms (user gets instant response!)")
print(f"    Speedup:      {sync_time/async_time:.0f}x faster user experience!")
print(f"    Queued tasks:  {task_q.qsize()} (processed in background)")

print()


# ================================================================
# 2. PRODUCER-CONSUMER — Work Queue Pattern
# ================================================================

print("=" * 60)
print("  2. PRODUCER-CONSUMER — Task Distribution")
print("=" * 60)


@dataclass
class Message:
    id: str
    body: dict
    attempts: int = 0
    created_at: float = field(default_factory=time.time)


class SimpleQueue:
    """Simulates a message queue with ACK/NACK."""

    def __init__(self, name: str, max_retries: int = 3):
        self.name = name
        self.queue = queue.Queue()
        self.dlq = queue.Queue()  # Dead Letter Queue
        self.max_retries = max_retries
        self.published = 0
        self.consumed = 0
        self.failed = 0
        self.lock = threading.Lock()

    def publish(self, message: Message):
        self.queue.put(message)
        with self.lock:
            self.published += 1

    def consume(self, timeout: float = 0.1) -> Message | None:
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def acknowledge(self, message: Message):
        with self.lock:
            self.consumed += 1

    def reject(self, message: Message):
        """Reject message — retry or send to DLQ."""
        message.attempts += 1
        if message.attempts < self.max_retries:
            self.queue.put(message)  # Retry
        else:
            self.dlq.put(message)   # Dead Letter Queue
            with self.lock:
                self.failed += 1


# Producer: sends 100 tasks
mq = SimpleQueue("photo_tasks", max_retries=3)

print(f"\n  --- Producer: Sending 100 photo resize tasks ---")
for i in range(100):
    msg = Message(f"msg_{i}", {"task": "resize", "photo_id": i})
    mq.publish(msg)
print(f"    Published: {mq.published} messages")

# Consumers: process tasks concurrently
print(f"\n  --- 3 Consumers processing tasks ---")
consumer_stats = defaultdict(int)


def consumer_worker(worker_id: int, mq: SimpleQueue):
    while True:
        msg = mq.consume(timeout=0.05)
        if msg is None:
            break

        # Simulate processing (with 10% failure rate)
        if random.random() < 0.10:
            mq.reject(msg)  # Failed — will retry
        else:
            time.sleep(0.005)  # Process for 5ms
            mq.acknowledge(msg)
            consumer_stats[worker_id] += 1


start = time.perf_counter()
threads = []
for i in range(3):
    t = threading.Thread(target=consumer_worker, args=(i + 1, mq))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

elapsed = (time.perf_counter() - start) * 1000

print(f"    Processing time: {elapsed:.0f}ms")
print(f"    Successfully processed: {mq.consumed}")
print(f"    Sent to DLQ (failed 3x): {mq.failed}")
print(f"    DLQ size: {mq.dlq.qsize()} messages")
print(f"\n    Per-consumer distribution:")
for worker_id, count in sorted(consumer_stats.items()):
    bar = "█" * (count // 2)
    print(f"      Consumer {worker_id}: {count:>3} tasks {bar}")

print()


# ================================================================
# 3. PUB/SUB — One Event, Multiple Subscribers
# ================================================================

print("=" * 60)
print("  3. PUB/SUB — Event Broadcasting")
print("=" * 60)


class PubSubBroker:
    """Simulates a publish-subscribe message broker."""

    def __init__(self):
        self.topics = defaultdict(list)  # topic → [subscriber callbacks]
        self.delivered = defaultdict(int)

    def subscribe(self, topic: str, subscriber_name: str, callback):
        self.topics[topic].append((subscriber_name, callback))

    def publish(self, topic: str, event: dict):
        for sub_name, callback in self.topics[topic]:
            callback(event)
            self.delivered[sub_name] += 1


broker = PubSubBroker()

# Subscribe multiple services to "order_placed" event
events_received = defaultdict(list)

broker.subscribe("order_placed", "Inventory",
                 lambda e: events_received["Inventory"].append(f"Reserved items for order {e['order_id']}"))
broker.subscribe("order_placed", "Payment",
                 lambda e: events_received["Payment"].append(f"Charged ${e['total']} for order {e['order_id']}"))
broker.subscribe("order_placed", "Notification",
                 lambda e: events_received["Notification"].append(f"Emailed user for order {e['order_id']}"))
broker.subscribe("order_placed", "Analytics",
                 lambda e: events_received["Analytics"].append(f"Logged conversion for order {e['order_id']}"))

# Publish one event
print(f"\n  --- Publishing 'order_placed' event ---")
broker.publish("order_placed", {"order_id": "ORD-001", "total": 299.99, "user": "Alice"})
broker.publish("order_placed", {"order_id": "ORD-002", "total": 149.50, "user": "Bob"})

print(f"    Published 2 events to 4 subscribers\n")
for service, events in events_received.items():
    print(f"    {service}:")
    for event in events:
        print(f"      {event}")

print(f"\n    Each event triggered {len(events_received)} independent actions!")
print(f"    Services are DECOUPLED — adding a new subscriber requires ZERO changes to producer")

print()


# ================================================================
# 4. DELIVERY GUARANTEES — Idempotency
# ================================================================

print("=" * 60)
print("  4. IDEMPOTENCY — Safe to Process Twice")
print("=" * 60)


class PaymentProcessor:
    """Demonstrates idempotent vs non-idempotent processing."""

    def __init__(self):
        self.balance = 1000.00
        self.processed_ids = set()  # Idempotency tracking

    def process_non_idempotent(self, payment_id: str, amount: float):
        """BAD: Not idempotent — double-charges on retry!"""
        self.balance -= amount
        return self.balance

    def process_idempotent(self, payment_id: str, amount: float):
        """GOOD: Idempotent — safe to call multiple times."""
        if payment_id in self.processed_ids:
            return self.balance  # Already processed, skip!

        self.balance -= amount
        self.processed_ids.add(payment_id)
        return self.balance


# Non-idempotent: message delivered twice → double charge!
print(f"\n  --- BAD: Non-Idempotent Consumer ---")
bad_processor = PaymentProcessor()
print(f"    Starting balance: ${bad_processor.balance:.2f}")
bad_processor.process_non_idempotent("pay_001", 100)
print(f"    After payment 1:  ${bad_processor.balance:.2f}")
bad_processor.process_non_idempotent("pay_001", 100)  # DUPLICATE!
print(f"    After DUPLICATE:  ${bad_processor.balance:.2f} (charged TWICE!)")

# Idempotent: duplicate safely ignored
print(f"\n  --- GOOD: Idempotent Consumer ---")
good_processor = PaymentProcessor()
print(f"    Starting balance: ${good_processor.balance:.2f}")
good_processor.process_idempotent("pay_001", 100)
print(f"    After payment 1:  ${good_processor.balance:.2f}")
good_processor.process_idempotent("pay_001", 100)  # Duplicate safely ignored!
print(f"    After DUPLICATE:  ${good_processor.balance:.2f} (correctly ignored!)")

print()


# ================================================================
# 5. BACKPRESSURE — When Producers Are Faster
# ================================================================

print("=" * 60)
print("  5. BACKPRESSURE — Producer vs Consumer Speed")
print("=" * 60)


def simulate_backpressure(producer_rate: int, consumer_rate: int,
                          duration_sec: float = 2.0, max_queue: int = 1000):
    """Simulate producer-consumer with different speeds."""
    q = queue.Queue(maxsize=max_queue)
    produced = 0
    consumed = 0
    dropped = 0
    max_queue_size = 0
    stop_event = threading.Event()

    def producer():
        nonlocal produced, dropped
        interval = 1.0 / producer_rate
        while not stop_event.is_set():
            try:
                q.put_nowait(f"msg_{produced}")
                produced += 1
            except queue.Full:
                dropped += 1
            time.sleep(interval)

    def consumer():
        nonlocal consumed
        interval = 1.0 / consumer_rate
        while not stop_event.is_set():
            try:
                q.get_nowait()
                consumed += 1
            except queue.Empty:
                pass
            time.sleep(interval)

    prod_thread = threading.Thread(target=producer, daemon=True)
    cons_thread = threading.Thread(target=consumer, daemon=True)
    prod_thread.start()
    cons_thread.start()

    # Monitor queue size
    for _ in range(int(duration_sec * 10)):
        time.sleep(0.1)
        max_queue_size = max(max_queue_size, q.qsize())

    stop_event.set()
    prod_thread.join(timeout=1)
    cons_thread.join(timeout=1)

    return produced, consumed, dropped, max_queue_size


print(f"\n  Queue max capacity: 1,000 messages")
print(f"\n  {'Scenario':<28} {'Produced':>10} {'Consumed':>10} {'Dropped':>9} {'Max Queue':>10}")
print(f"  {'─'*28} {'─'*10} {'─'*10} {'─'*9} {'─'*10}")

scenarios = [
    ("Balanced (500/500)",       500, 500),
    ("Slight overload (800/500)", 800, 500),
    ("Heavy overload (2000/500)", 2000, 500),
    ("Consumer faster (500/800)", 500, 800),
]

for name, prod_rate, cons_rate in scenarios:
    produced, consumed, dropped, max_q = simulate_backpressure(prod_rate, cons_rate)
    status = "DROPPING!" if dropped > 0 else "OK" if max_q < 500 else "FILLING"
    print(f"  {name:<28} {produced:>10} {consumed:>10} {dropped:>9} {max_q:>10} {status}")

print(f"""
  SOLUTIONS FOR BACKPRESSURE:
    1. Add more consumers (horizontal scaling)
    2. Rate-limit the producer
    3. Increase queue size (Kafka: use disk, virtually unlimited)
    4. Drop low-priority messages
    5. Auto-scale consumers based on queue depth""")

print()


# ================================================================
# 6. QUEUE DEPTH MONITORING — Auto-Scaling Signal
# ================================================================

print("=" * 60)
print("  6. QUEUE DEPTH — Auto-Scaling Trigger")
print("=" * 60)

print(f"\n  Simulating queue depth over time with auto-scaling:")
print(f"\n  {'Time':>6} {'Queue':>7} {'Consumers':>11} {'Visual'}")
print(f"  {'─'*6} {'─'*7} {'─'*11} {'─'*35}")

queue_depth = 0
consumers = 2
incoming_rates = [100, 100, 300, 500, 800, 800, 500, 200, 100, 50]

for t, incoming in enumerate(incoming_rates):
    processing = consumers * 100  # Each consumer handles 100/sec
    queue_depth = max(0, queue_depth + incoming - processing)

    # Auto-scale based on queue depth
    if queue_depth > 500 and consumers < 10:
        consumers += 2
        scale_event = " SCALE UP!"
    elif queue_depth < 50 and consumers > 2:
        consumers -= 1
        scale_event = " scale down"
    else:
        scale_event = ""

    bar = "█" * min(queue_depth // 20, 30)
    print(f"  t={t:>3}s {queue_depth:>7} {consumers:>9}    {bar}{scale_event}")

print(f"""
  KEY: Queue depth is the #1 metric for auto-scaling consumers.
  Deep queue → add consumers. Empty queue → reduce consumers.
  This is how AWS Lambda, K8s KEDA, and Celery auto-scale.""")


print("\n" + "=" * 60)
print("  System Design Topic 11 Complete!")
print("  Say 'next' for Topic 12: API Design & Protocols")
print("=" * 60)
