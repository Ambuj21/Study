# 📘 Topic 1.2 — Algorithm Thinking & Big-O Notation

> **Code Implementation**: See [code.py](./code.py) for runnable Python implementation

> **Why this matters**: Two developers can solve the same problem — one's code runs in **1 second**, the other takes **3 hours**. The difference? They chose different algorithms. Big-O is the language that lets you **predict** which one is faster *before you even run the code*.

---

## 🧠 What Is Big-O? — The Speedometer for Code

### 🎯 Real-World Analogy

> Imagine you're looking for a friend in a crowd:
> - **O(1)**: Your friend is wearing a **bright red hat**. You spot them instantly. Crowd size doesn't matter.
> - **O(n)**: You scan **every single face** one by one. Bigger crowd = longer search.
> - **O(n²)**: You compare **every person with every other person** to find twins. Nightmare in a big crowd.

### 📊 The Growth Chart — How Algorithms Scale

Each row below shows how many **operations** an algorithm needs as the input grows. Watch how the bad ones explode!

```mermaid
graph LR
    A1["🟢 O(1)<br/>Constant"] --> B1["n=10: 1"] --> C1["n=1K: 1"] --> D1["n=1M: 1 ✅"]

    style A1 fill:#2ecc71,stroke:#333,color:#fff
    style B1 fill:#2ecc71,stroke:#333,color:#fff
    style C1 fill:#2ecc71,stroke:#333,color:#fff
    style D1 fill:#2ecc71,stroke:#333,color:#fff
```

```mermaid
graph LR
    A2["🔵 O(log n)<br/>Logarithmic"] --> B2["n=10: 3"] --> C2["n=1K: 10"] --> D2["n=1M: 20 ✅"]

    style A2 fill:#3498db,stroke:#333,color:#fff
    style B2 fill:#3498db,stroke:#333,color:#fff
    style C2 fill:#3498db,stroke:#333,color:#fff
    style D2 fill:#3498db,stroke:#333,color:#fff
```

```mermaid
graph LR
    A3["🟡 O(n)<br/>Linear"] --> B3["n=10: 10"] --> C3["n=1K: 1,000"] --> D3["n=1M: 1,000,000 ⚡"]

    style A3 fill:#f1c40f,stroke:#333,color:#333
    style B3 fill:#f1c40f,stroke:#333,color:#333
    style C3 fill:#f1c40f,stroke:#333,color:#333
    style D3 fill:#f1c40f,stroke:#333,color:#333
```

```mermaid
graph LR
    A4["🟠 O(n log n)<br/>Linearithmic"] --> B4["n=10: 33"] --> C4["n=1K: 10,000"] --> D4["n=1M: 20,000,000 ⚠️"]

    style A4 fill:#e67e22,stroke:#333,color:#fff
    style B4 fill:#e67e22,stroke:#333,color:#fff
    style C4 fill:#e67e22,stroke:#333,color:#fff
    style D4 fill:#e67e22,stroke:#333,color:#fff
```

```mermaid
graph LR
    A5["🔴 O(n²)<br/>Quadratic"] --> B5["n=10: 100"] --> C5["n=1K: 1,000,000"] --> D5["n=1M: 1,000,000,000,000 💀"]

    style A5 fill:#e74c3c,stroke:#333,color:#fff
    style B5 fill:#e74c3c,stroke:#333,color:#fff
    style C5 fill:#e74c3c,stroke:#333,color:#fff
    style D5 fill:#e74c3c,stroke:#333,color:#fff
```

### Summary Table

| Big-O | Name | n = 10 | n = 1,000 | n = 1,000,000 | Verdict |
|-------|------|--------|-----------|---------------|---------|
| 🟢 O(1) | Constant | 1 | 1 | 1 | ✅ Perfect |
| 🔵 O(log n) | Logarithmic | 3 | 10 | 20 | ✅ Excellent |
| 🟡 O(n) | Linear | 10 | 1,000 | 1,000,000 | ⚡ Good |
| 🟠 O(n log n) | Linearithmic | 33 | 10,000 | 20,000,000 | ⚠️ Acceptable |
| 🔴 O(n²) | Quadratic | 100 | 1,000,000 | 1,000,000,000,000 | 💀 Terrible |

> **Key Insight**: At n = 1,000,000 items, an O(n²) algorithm does **1 TRILLION** operations. An O(n) algorithm does just **1 million**. That's a **1,000,000x** difference!

---

## 🟢 O(1) — Constant Time: "I Don't Care How Big It Is"

### 📊 Visual

```mermaid
graph LR
    subgraph "O(1) — Always the same speed"
        I10["📦 10 items<br/>⏱️ 1 step"] ~~~ I1000["📦 1,000 items<br/>⏱️ 1 step"] ~~~ I1M["📦 1,000,000 items<br/>⏱️ 1 step"]
    end

    style I10 fill:#2ecc71,stroke:#333,color:#fff
    style I1000 fill:#2ecc71,stroke:#333,color:#fff
    style I1M fill:#2ecc71,stroke:#333,color:#fff
```

### 🎯 Analogy
> Opening a **book to page 50**. Whether the book has 100 pages or 10,000 pages, flipping to page 50 takes the same time.

### 💻 Pseudo Code Examples

```text
// All O(1) — instant regardless of size

my_list = [10, 20, 30, 40, 50]
my_dictionary = {"name": "Alice", "age": 28}

// ✅ Access by index
first = my_list[0]              // O(1)

// ✅ Dictionary lookup
name = my_dictionary["name"]    // O(1)

// ✅ Append to list
my_list.APPEND(60)              // O(1)

// ✅ Check dictionary key
exists = HAS_KEY(my_dictionary, "name") // O(1)

// ✅ Get length
size = LENGTH(my_list)          // O(1)

// ✅ Push/pop from stack
my_list.POP()                   // O(1)
```

---

## 🔵 O(log n) — Logarithmic: "I Cut the Problem in Half Each Step"

### 📊 Visual — Binary Search in Action

```mermaid
graph TD
    subgraph "🔍 Finding 67 in a sorted list of 16 numbers"
        S1["Step 1: Look at middle<br/>[1, 3, 5, 8, 12, 25, 34, ❓50❓, 56, 67, 72, 81, 90, 95, 98, 100]<br/>67 > 50 → go RIGHT ➡️"]
        S2["Step 2: Right half<br/>[56, 67, 72, ❓81❓, 90, 95, 98, 100]<br/>67 < 81 → go LEFT ⬅️"]
        S3["Step 3: Left portion<br/>[56, ❓67❓, 72]<br/>67 == 67 → ✅ FOUND!"]
    end

    S1 --> S2 --> S3

    style S1 fill:#3498db,stroke:#333,color:#fff
    style S2 fill:#2980b9,stroke:#333,color:#fff
    style S3 fill:#2ecc71,stroke:#333,color:#fff,stroke-width:3px
```

> **16 items → only 3 steps!** Each step eliminates **half** the remaining data.
> - 1,000 items → ~10 steps
> - 1,000,000 items → ~20 steps
> - 1,000,000,000 items → ~30 steps

### 🎯 Analogy
> The **dictionary word game**: "I'm thinking of a word. Is it before or after 'M'?"
> Each guess eliminates half the dictionary. You find any word in ~17 guesses out of 100,000 words!

### 💻 Pseudo Code — Binary Search

```text
FUNCTION binary_search(sorted_list, target):
    // Find target in a sorted list. Returns index or -1.
    left = 0
    right = LENGTH(sorted_list) - 1
    steps = 0

    WHILE left <= right:
        steps = steps + 1
        mid = (left + right) / 2

        IF sorted_list[mid] == target:
            PRINT "Found target at index", mid, "in", steps, "steps!"
            RETURN mid
        ELSE IF sorted_list[mid] < target:
            left = mid + 1     // Target is in right half
        ELSE:
            right = mid - 1    // Target is in left half

    PRINT "Target not found after", steps, "steps"
    RETURN -1
```

---

## 🟡 O(n) — Linear: "I Check Everything Once"

### 📊 Visual

```mermaid
graph LR
    subgraph "O(n) — Check each item once"
        A["🔍 Item 1<br/>Not it"] --> B["🔍 Item 2<br/>Not it"] --> C["🔍 Item 3<br/>Not it"] --> D["🔍 ...<br/>..."] --> E["🔍 Item n<br/>Maybe?"]
    end

    style A fill:#f1c40f,stroke:#333,color:#333
    style B fill:#f1c40f,stroke:#333,color:#333
    style C fill:#f1c40f,stroke:#333,color:#333
    style D fill:#f1c40f,stroke:#333,color:#333
    style E fill:#f1c40f,stroke:#333,color:#333
```

### 🎯 Analogy
> **Reading a guest list** to find if your name is on it. You start from the top and read each name. 100 guests? Check up to 100 names.

### 💻 Pseudo Code Examples

```text
// All O(n) — touch each element once

numbers = [4, 2, 7, 1, 9, 3, 8, 5, 6]

// ✅ Linear search
FUNCTION find_number(nums, target):
    FOR i = 0 TO LENGTH(nums) - 1:
        IF nums[i] == target:
            RETURN i
    RETURN -1

// ✅ Find maximum
FUNCTION find_max(nums):
    max_val = nums[0]
    FOR EACH num IN nums:       // Visit each element once
        IF num > max_val:
            max_val = num
    RETURN max_val

// ✅ Sum all elements
FUNCTION sum_all(nums):
    total = 0
    FOR EACH num IN nums:
        total = total + num
    RETURN total                  // O(n) — adds each number once
```

---

## 🟠 O(n log n) — Linearithmic: "I Sort Things Efficiently"

### 📊 Visual — Merge Sort: Divide and Conquer

```mermaid
graph TD
    A["[38, 27, 43, 3, 9, 82, 10]"] --> B["[38, 27, 43, 3]"]
    A --> C["[9, 82, 10]"]

    B --> D["[38, 27]"]
    B --> E["[43, 3]"]
    C --> F["[9, 82]"]
    C --> G["[10]"]

    D --> D1["[38]"]
    D --> D2["[27]"]
    E --> E1["[43]"]
    E --> E2["[3]"]
    F --> F1["[9]"]
    F --> F2["[82]"]

    D1 & D2 -->|merge| M1["[27, 38]"]
    E1 & E2 -->|merge| M2["[3, 43]"]
    F1 & F2 -->|merge| M3["[9, 82]"]

    M1 & M2 -->|merge| M4["[3, 27, 38, 43]"]
    M3 & G -->|merge| M5["[9, 10, 82]"]

    M4 & M5 -->|merge| FINAL["✅ [3, 9, 10, 27, 38, 43, 82]"]

    style A fill:#e74c3c,stroke:#333,color:#fff
    style FINAL fill:#2ecc71,stroke:#333,color:#fff,stroke-width:3px
    style M1 fill:#3498db,stroke:#333,color:#fff
    style M2 fill:#3498db,stroke:#333,color:#fff
    style M3 fill:#3498db,stroke:#333,color:#fff
    style M4 fill:#9b59b6,stroke:#333,color:#fff
    style M5 fill:#9b59b6,stroke:#333,color:#fff
```

> **Why O(n log n)?**
> - **log n levels** of splitting (each split halves the data)
> - **n work** at each level (merging all elements)
> - Total: n × log n

### 🎯 Analogy
> **Sorting exams**: Split the pile in half, split again, sort tiny piles, then merge them back in order. Much faster than comparing every paper to every other paper!

### 💻 Pseudo Code

```text
// Most efficient modern sorting algorithms are O(n log n)
numbers = [38, 27, 43, 3, 9, 82, 10]

sorted_nums = SORT(numbers)           // Returns new sorted list

// Both are O(n log n) — very efficient!
```

---

## 🔴 O(n²) — Quadratic: "I Compare Everything with Everything"

### 📊 Visual — Why It's So Slow

```mermaid
graph TD
    subgraph "🔴 O(n²) — Each element checks ALL others"
        A["Item 1"] --> B1["vs Item 2"]
        A --> B2["vs Item 3"]
        A --> B3["vs Item 4"]
        A --> B4["vs Item 5"]

        C["Item 2"] --> D1["vs Item 1"]
        C --> D2["vs Item 3"]
        C --> D3["vs Item 4"]
        C --> D4["vs Item 5"]

        E["Item 3"] --> F1["vs Item 1"]
        E --> F2["vs Item 2"]
        E --> F3["vs Item 4"]
        E --> F4["vs Item 5"]
    end

    style A fill:#e74c3c,stroke:#333,color:#fff
    style C fill:#e74c3c,stroke:#333,color:#fff
    style E fill:#e74c3c,stroke:#333,color:#fff
```

> 5 items = 25 comparisons. 1,000 items = 1,000,000 comparisons. **It explodes!**

### 🎯 Analogy
> **Handshake problem**: At a party of 100 people, if everyone shakes hands with everyone else, that's ~5,000 handshakes. At 1,000 people, it's ~500,000!

### 💻 Pseudo Code — Spot the O(n²) Traps!

```text
// ❌ TRAP 1: Nested loops
FUNCTION has_duplicate_slow(nums):
    // O(n²) — compares every pair
    FOR i = 0 TO LENGTH(nums) - 1:
        FOR j = i + 1 TO LENGTH(nums) - 1:
            IF nums[i] == nums[j]:
                RETURN True
    RETURN False


// ✅ FIX: Use a Hash Set!
FUNCTION has_duplicate_fast(nums):
    // O(n) — checks each element once
    seen = NEW HASH_SET()
    FOR EACH num IN nums:
        IF seen.CONTAINS(num): // O(1) lookup in set!
            RETURN True
        seen.ADD(num)
    RETURN False


// ❌ TRAP 2: Linear search inside a loop
FUNCTION common_elements_slow(list_a, list_b):
    // O(n²) — search in list is O(n), and it's inside a loop
    result = NEW LIST()
    FOR EACH item IN list_a:
        IF list_b.CONTAINS(item): // O(n) for each check!
            result.APPEND(item)
    RETURN result


// ✅ FIX: Convert to set first
FUNCTION common_elements_fast(list_a, list_b):
    // O(n) — lookup in set is O(1)
    set_b = NEW HASH_SET(list_b)  // O(n) once
    result = NEW LIST()
    FOR EACH item IN list_a:
        IF set_b.CONTAINS(item):  // O(1) for each check!
            result.APPEND(item)
    RETURN result
```

---

## 🧮 The Big-O Rules — How to Calculate

### Rule 1: Drop Constants

```mermaid
graph LR
    A["O(2n)"] -->|simplify| B["O(n)"]
    C["O(n/2)"] -->|simplify| D["O(n)"]
    E["O(500)"] -->|simplify| F["O(1)"]

    style B fill:#2ecc71,stroke:#333,color:#fff
    style D fill:#2ecc71,stroke:#333,color:#fff
    style F fill:#2ecc71,stroke:#333,color:#fff
```

> We care about the **growth pattern**, not the exact number. Whether you loop through the list 1 time or 3 times, it's still O(n).

### Rule 2: Drop Smaller Terms

```mermaid
graph LR
    A["O(n² + n)"] -->|drop n| B["O(n²)"]
    C["O(n + log n)"] -->|drop log n| D["O(n)"]
    E["O(n³ + n² + n)"] -->|drop n² + n| F["O(n³)"]

    style B fill:#2ecc71,stroke:#333,color:#fff
    style D fill:#2ecc71,stroke:#333,color:#fff
    style F fill:#2ecc71,stroke:#333,color:#fff
```

> At large n, the biggest term **dominates**. n² + n ≈ n² when n is a million.

### Rule 3: Different Inputs = Different Variables

```text
// This is O(a * b), NOT O(n²)!
FUNCTION print_pairs(list_a, list_b):
    FOR EACH a IN list_a:        // O(a)
        FOR EACH b IN list_b:    // O(b)
            PRINT a, b
// Only O(n²) if list_a and list_b are the same size
```

### 🧩 Quick Analysis Cheat Sheet

```mermaid
graph TD
    Q1{"Single loop<br/>over n items?"} -->|Yes| A1["O(n)"]
    Q2{"Nested loop<br/>both over n?"} -->|Yes| A2["O(n²)"]
    Q3{"Halving the data<br/>each step?"} -->|Yes| A3["O(log n)"]
    Q4{"Sorting then<br/>scanning?"} -->|Yes| A4["O(n log n)"]
    Q5{"No loops,<br/>direct access?"} -->|Yes| A5["O(1)"]
    Q6{"Loop with binary<br/>search inside?"} -->|Yes| A6["O(n log n)"]

    style A1 fill:#f1c40f,stroke:#333,color:#333
    style A2 fill:#e74c3c,stroke:#333,color:#fff
    style A3 fill:#3498db,stroke:#333,color:#fff
    style A4 fill:#e67e22,stroke:#333,color:#fff
    style A5 fill:#2ecc71,stroke:#333,color:#fff
    style A6 fill:#e67e22,stroke:#333,color:#fff
```

---

## 🔥 Common Algorithm Patterns

### Pattern 1: Two Pointers

```mermaid
graph LR
    subgraph "Two pointers moving inward"
        L["L →"] --- A["1"] --- B["3"] --- C["5"] --- D["7"] --- E["9"] --- R["← R"]
    end

    style L fill:#3498db,stroke:#333,color:#fff
    style R fill:#e74c3c,stroke:#333,color:#fff
```

```text
FUNCTION two_sum_sorted(nums, target):
    // Find two numbers that add to target in a SORTED list. O(n)
    left = 0
    right = LENGTH(nums) - 1

    WHILE left < right:
        current_sum = nums[left] + nums[right]
        IF current_sum == target:
            RETURN [left, right]
        ELSE IF current_sum < target:
            left = left + 1    // Need bigger sum → move left pointer right
        ELSE:
            right = right - 1  // Need smaller sum → move right pointer left

    RETURN []

// [1, 3, 5, 7, 9], target=12 → [1, 4] because 3 + 9 = 12
```

### Pattern 2: Sliding Window

```mermaid
graph LR
    subgraph "Window slides across the array"
        A["2"] --- B["1"] --- C["5"] --- D["1"] --- E["3"] --- F["2"]
    end

    subgraph "Window of size 3"
        W1["[2,1,5]=8"] --> W2["[1,5,1]=7"] --> W3["[5,1,3]=9 ✅ max"] --> W4["[1,3,2]=6"]
    end

    style W3 fill:#2ecc71,stroke:#333,color:#fff,stroke-width:3px
```

```text
FUNCTION max_sum_subarray(nums, k):
    // Find max sum of any k consecutive elements. O(n)
    // Calculate first window
    window_sum = 0
    FOR i = 0 TO k - 1:
        window_sum = window_sum + nums[i]
    max_sum = window_sum

    // Slide the window: add new element, remove old one
    FOR i = k TO LENGTH(nums) - 1:
        window_sum = window_sum + nums[i] - nums[i - k]    // Slide!
        max_sum = MAX(max_sum, window_sum)

    RETURN max_sum

// [2, 1, 5, 1, 3, 2], k=3 → 9 (subarray [5, 1, 3])
```

### Pattern 3: Frequency Counter

```text
FUNCTION are_anagrams(word1, word2):
    // Check if two words are anagrams. O(n)
    count_map1 = GET_CHARACTER_COUNTS(word1)
    count_map2 = GET_CHARACTER_COUNTS(word2)
    RETURN count_map1 == count_map2

// "listen" and "silent" → True
// "hello" and "world" → False

// GET_CHARACTER_COUNTS("listen") → {'l':1, 'i':1, 's':1, 't':1, 'e':1, 'n':1}
// GET_CHARACTER_COUNTS("silent") → {'s':1, 'i':1, 'l':1, 'e':1, 'n':1, 't':1}
// Same counts = anagram!
```

---

## ⏱️ Space Complexity — Memory Matters Too!

```mermaid
graph TD
    subgraph "Time vs Space Trade-off"
        A["🐌 Slow + 💾 No extra memory<br/>O(n²) time, O(1) space<br/>e.g., Bubble Sort"] ---|"Trade-off"| B["🚀 Fast + 💾 Extra memory<br/>O(n) time, O(n) space<br/>e.g., Hash Set lookup"]
    end

    style A fill:#e74c3c,stroke:#333,color:#fff
    style B fill:#2ecc71,stroke:#333,color:#fff
```

```text
// O(1) space — uses no extra memory proportional to input
FUNCTION find_max(nums):
    max_val = nums[0]         // Just one variable, regardless of input size
    FOR EACH num IN nums:
        max_val = MAX(max_val, num)
    RETURN max_val

// O(n) space — creates a new collection proportional to input
FUNCTION remove_duplicates(nums):
    unique_set = NEW HASH_SET()
    FOR EACH num IN nums:
        unique_set.ADD(num)
    RETURN unique_set.TO_LIST() // The list can be as large as nums
```

---

## 📋 The Complete Big-O Reference

| Big-O | Name | Example | 1K items | 1M items | Verdict |
|-------|------|---------|----------|----------|---------|
| O(1) | Constant | Dict lookup | 1 | 1 | 🟢 Perfect |
| O(log n) | Logarithmic | Binary search | 10 | 20 | 🟢 Excellent |
| O(n) | Linear | Single loop | 1,000 | 1,000,000 | 🟡 Good |
| O(n log n) | Linearithmic | Sorting | 10,000 | 20,000,000 | 🟡 Acceptable |
| O(n²) | Quadratic | Nested loops | 1,000,000 | 1,000,000,000,000 | 🔴 Bad |
| O(2ⁿ) | Exponential | All subsets | 2^1000 💀 | ∞ | 💀 Terrible |
| O(n!) | Factorial | All permutations | 💀 | ☠️ | ☠️ Never |

---

## 🏋️ Practice Exercises

### Exercise 1: What's the Big-O? (Analyze These)

```text
// a) What's the Big-O?
FUNCTION mystery_a(n):
    FOR i = 0 TO n - 1:
        PRINT i

// b) What's the Big-O?
FUNCTION mystery_b(n):
    FOR i = 0 TO n - 1:
        FOR j = 0 TO n - 1:
            PRINT i, j

// c) What's the Big-O?
FUNCTION mystery_c(n):
    i = n
    WHILE i > 0:
        PRINT i
        i = i / 2

// d) What's the Big-O?
FUNCTION mystery_d(nums):
    SORT(nums)                   // ?
    RETURN nums[0]               // ?

// e) What's the Big-O?
FUNCTION mystery_e(nums):
    seen = NEW HASH_SET()
    FOR EACH num IN nums:        // ?
        IF seen.CONTAINS(num):   // ?
            RETURN True
        seen.ADD(num)
    RETURN False
```

### Exercise 2: Optimize This! (Turn O(n²) → O(n))

```text
// This is O(n²). Can you make it O(n)?
FUNCTION find_pair_with_sum(nums, target):
    FOR i = 0 TO LENGTH(nums) - 1:
        FOR j = i + 1 TO LENGTH(nums) - 1:
            IF nums[i] + nums[j] == target:
                RETURN [i, j]
    RETURN []
```

### Exercise 3: Binary Search Practice

```text
// Implement binary search to find the first number >= target
// Input: [1, 3, 5, 7, 9, 11], target=6 → Output: index 3 (value 7)
```

---

## 🎤 Interview Corner

> **Q: "What's the time complexity of this code?"**
> This is the **#1 most asked** follow-up in coding interviews. Practice analyzing every piece of code you write!

> **Q: "Can you optimize this from O(n²) to O(n)?"**
> **Strategy**: 90% of the time, the answer is **use a hash map/set** to trade space for time.

> **Q: "What's the difference between time and space complexity?"**
> **Great answer**: "Time complexity measures how the number of operations grows with input. Space complexity measures how much extra memory we use. Often there's a trade-off — we can use extra memory (like a hash set) to make the algorithm faster."

---

## ✅ Key Takeaways

| Lesson | Remember |
|--------|----------|
| Big-O measures **growth rate** | Not exact time, but how it **scales** |
| Drop constants and small terms | O(2n + 5) → O(n) |
| Nested loops = multiply | Loop in loop = O(n × n) = O(n²) |
| Halving = logarithmic | Binary search = O(log n) |
| Hash maps fix O(n²) | If you see nested search, use a dict/set |
| Space-time trade-off | Use more memory → get faster algorithms |

---

**Next up → [Topic 1.3: How the Internet Actually Works](../1.3-How-Internet-Works/)**
