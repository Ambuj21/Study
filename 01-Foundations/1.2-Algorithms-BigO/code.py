"""
📘 Topic 1.2 — Algorithm Thinking & Big-O Notation: Hands-On Practice
Run this file to see algorithms in action with timing comparisons!

Usage:
    set PYTHONIOENCODING=utf-8
    python examples.py
"""
import time


# ═══════════════════════════════════════════════════
# 1. O(1) vs O(n) vs O(n^2) — Feel the Difference
# ═══════════════════════════════════════════════════

print("=" * 60)
print("  O(1) vs O(n) vs O(n^2) — LIVE COMPARISON")
print("=" * 60)

n = 10_000
data_list = list(range(n))
data_dict = {i: True for i in range(n)}


# O(1) — Dictionary lookup
start = time.perf_counter()
_ = data_dict[9999]
t_o1 = time.perf_counter() - start
print(f"  O(1)   Dict lookup:           {t_o1:.8f}s")


# O(n) — Linear search
start = time.perf_counter()
_ = 9999 in data_list
t_on = time.perf_counter() - start
print(f"  O(n)   List search:            {t_on:.8f}s")


# O(n^2) — Nested loop (check all pairs)
start = time.perf_counter()
small_list = list(range(500))  # Using smaller n to not freeze
count = 0
for i in small_list:
    for j in small_list:
        count += 1
t_on2 = time.perf_counter() - start
print(f"  O(n^2) Nested loop (n=500):    {t_on2:.8f}s  ({count:,} operations)")
print()


# ═══════════════════════════════════════════════════
# 2. BINARY SEARCH — O(log n) Magic
# ═══════════════════════════════════════════════════

print("=" * 60)
print("  BINARY SEARCH — O(log n) vs Linear Search O(n)")
print("=" * 60)


def binary_search(sorted_list, target):
    """O(log n) — Halves the search space each step."""
    left, right = 0, len(sorted_list) - 1
    steps = 0

    while left <= right:
        steps += 1
        mid = (left + right) // 2
        if sorted_list[mid] == target:
            return mid, steps
        elif sorted_list[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1, steps


def linear_search(data, target):
    """O(n) — Checks every element."""
    steps = 0
    for i, val in enumerate(data):
        steps += 1
        if val == target:
            return i, steps
    return -1, steps


# Compare on different sizes
print(f"  {'Size':>12} | {'Linear Steps':>14} | {'Binary Steps':>14} | {'Speedup':>10}")
print(f"  {'-'*12} | {'-'*14} | {'-'*14} | {'-'*10}")

for size in [100, 1_000, 10_000, 100_000, 1_000_000]:
    data = list(range(size))
    target = size - 5  # Near the end (worst case for linear)

    _, linear_steps = linear_search(data, target)
    _, binary_steps = binary_search(data, target)

    speedup = linear_steps / binary_steps if binary_steps > 0 else 0
    print(f"  {size:>12,} | {linear_steps:>14,} | {binary_steps:>14,} | {speedup:>9.0f}x")

print()


# ═══════════════════════════════════════════════════
# 3. THE O(n^2) TO O(n) OPTIMIZATION
# ═══════════════════════════════════════════════════

print("=" * 60)
print("  OPTIMIZATION: O(n^2) -> O(n) with Hash Map")
print("=" * 60)


def has_duplicate_slow(nums):
    """O(n^2) — Compare every pair."""
    comparisons = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            comparisons += 1
            if nums[i] == nums[j]:
                return True, comparisons
    return False, comparisons


def has_duplicate_fast(nums):
    """O(n) — Use a set for O(1) lookups."""
    seen = set()
    checks = 0
    for num in nums:
        checks += 1
        if num in seen:
            return True, checks
        seen.add(num)
    return False, checks


# Compare with duplicate at the end
sizes = [100, 500, 1000, 5000]
print(f"  {'Size':>8} | {'O(n^2) ops':>12} | {'O(n) ops':>10} | {'O(n^2) time':>12} | {'O(n) time':>12}")
print(f"  {'-'*8} | {'-'*12} | {'-'*10} | {'-'*12} | {'-'*12}")

for size in sizes:
    test_data = list(range(size))
    test_data.append(0)  # Duplicate of first element at the end

    start = time.perf_counter()
    _, slow_ops = has_duplicate_slow(test_data)
    slow_time = time.perf_counter() - start

    start = time.perf_counter()
    _, fast_ops = has_duplicate_fast(test_data)
    fast_time = time.perf_counter() - start

    print(f"  {size:>8,} | {slow_ops:>12,} | {fast_ops:>10,} | {slow_time:>11.6f}s | {fast_time:>11.6f}s")

print()


# ═══════════════════════════════════════════════════
# 4. SORTING — O(n log n) in Action
# ═══════════════════════════════════════════════════

print("=" * 60)
print("  SORTING — Python's Timsort O(n log n)")
print("=" * 60)

import random

print(f"  {'Size':>12} | {'Sort Time':>12}")
print(f"  {'-'*12} | {'-'*12}")

for size in [1_000, 10_000, 100_000, 1_000_000]:
    data = [random.randint(0, size) for _ in range(size)]

    start = time.perf_counter()
    data.sort()
    sort_time = time.perf_counter() - start

    print(f"  {size:>12,} | {sort_time:>11.6f}s")

print()


# ═══════════════════════════════════════════════════
# 5. ALGORITHM PATTERNS Demo
# ═══════════════════════════════════════════════════

print("=" * 60)
print("  PATTERN 1: Two Pointers")
print("=" * 60)


def two_sum_sorted(nums, target):
    """Find pair that sums to target in sorted list. O(n)"""
    left, right = 0, len(nums) - 1
    while left < right:
        s = nums[left] + nums[right]
        if s == target:
            return (nums[left], nums[right])
        elif s < target:
            left += 1
        else:
            right -= 1
    return None


sorted_nums = [1, 3, 5, 7, 9, 11, 15, 20]
result = two_sum_sorted(sorted_nums, 16)
print(f"  List: {sorted_nums}")
print(f"  Target: 16 -> Pair: {result}")
print()

print("=" * 60)
print("  PATTERN 2: Sliding Window")
print("=" * 60)


def max_sum_subarray(nums, k):
    """Find max sum of k consecutive elements. O(n)"""
    window_sum = sum(nums[:k])
    max_sum = window_sum
    best_start = 0

    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        if window_sum > max_sum:
            max_sum = window_sum
            best_start = i - k + 1

    return max_sum, nums[best_start:best_start + k]


data = [2, 1, 5, 1, 3, 2, 8, 1, 4]
max_s, subarray = max_sum_subarray(data, 3)
print(f"  List: {data}")
print(f"  Max sum of 3 consecutive: {max_s} -> subarray: {subarray}")
print()

print("=" * 60)
print("  PATTERN 3: Frequency Counter")
print("=" * 60)

from collections import Counter


def top_k_frequent(words, k):
    """Find k most frequent words. O(n log n)"""
    counts = Counter(words)
    return counts.most_common(k)


text = "python is great python is fast python is readable java is verbose java is typed"
words = text.split()
top_3 = top_k_frequent(words, 3)
print(f"  Text: '{text}'")
print(f"  Top 3 words: {top_3}")
print()


# ═══════════════════════════════════════════════════
# 6. EXERCISE ANSWERS
# ═══════════════════════════════════════════════════

print("=" * 60)
print("  EXERCISE ANSWERS")
print("=" * 60)
print()
print("  mystery_a: O(n)       -- single loop")
print("  mystery_b: O(n^2)     -- nested loop")
print("  mystery_c: O(log n)   -- halving each step")
print("  mystery_d: O(n log n) -- sort dominates the O(1) access")
print("  mystery_e: O(n)       -- single loop with O(1) set lookup")
print()

print("=" * 60)
print("  Topic 1.2 Complete!")
print("  Say 'next' for Topic 1.3: How the Internet Actually Works")
print("=" * 60)
