---
title: "Using Python Language Features and the Standard Library"
teaching: 10
exercises: 5
---

:::::::::::::::::::::::::::::::::::::: questions

- Why are Python loops slower than specialised functions?
- How can I make my code more readable and faster?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

- Able to utilise Python language features effectively
- Able to search Python documentation for functionality available in built-in types and in the standard library
- Able to identify when Python code can be rewritten to perform execution in the back-end.

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: instructor

This episode discusses relatively fundamental features of Python.

For students experienced with writing Python, many of these points may be unnecessary. However, self-taught students—especially if they have previously studied lower-level languages with a less powerful standard library—may have adopted "unpythonic" habits and will particularly benefit from this section.

::::::::::::::::::::::::::::::::::::::::::::::::

Before we look at data structures, algorithms and third-party libraries, it's worth reviewing the fundamentals of Python.
If you're familiar with other programming languages, like C or Delphi, you might not know the Pythonic approaches. Whilst you can write Python in a way similar to other languages, it is often more effective to take advantage of Python's principles and idioms.


## Built-in Functions

For example, you might think to sum a list of numbers by using a for loop, as would be typical in C, as shown in the function `manualSumC()` and `manualSumPy()` below. 

```Python
import random
from timeit import timeit

N = 100000  # Number of elements in the list

# Ensure every list is the same
random.seed(12)
my_data = [random.random() for i in range(N)]


def manualSumC():
    n = 0
    for i in range(len(my_data)):
        n += my_data[i]
    return n

def manualSumPy(): 
    n = 0
    for evt_count in my_data:
        n += evt_count
    return n

def builtinSum(): 
    return sum(my_data)


repeats = 1000
print(f"manualSumC: {timeit(manualSumC, globals=globals(), number=repeats):.3f}ms")
print(f"manualSumPy: {timeit(manualSumPy, globals=globals(), number=repeats):.3f}ms")
print(f"builtinSum: {timeit(builtinSum, globals=globals(), number=repeats):.3f}ms")
```

Even just replacing the iteration over indices (which may be a habit you’ve picked up if you first learned to program in C) with a more pythonic iteration over the elements themselves speeds up the code by about 2x.
But even better, by switching to the built-in `sum()` function our code becomes about 8x faster and much easier to read while doing the exact same operation!

```output
manualSumC: 1.624ms
manualSumPy: 0.740ms
builtinSum: 0.218ms
```

This is because [built-in functions](https://docs.python.org/3/library/functions.html) (i.e. those that are available without importing packages) are typically implemented in the CPython back-end, so their performance benefits from bypassing the Python interpreter.

In particular, those which are passed an `iterable` (e.g. lists) are likely to provide the greatest benefits to performance. The Python documentation provides equivalent Python code for many of these cases.

* [`all()`](https://docs.python.org/3/library/functions.html#all): boolean and of all items
* [`any()`](https://docs.python.org/3/library/functions.html#all): boolean or of all items
* [`max()`](https://docs.python.org/3/library/functions.html#max): Return the maximum item 
* [`min()`](https://docs.python.org/3/library/functions.html#min): Return the minimum item 
* [`sum()`](https://docs.python.org/3/library/functions.html#sum): Return the sum of all items

<!-- todo exercise/s where pure-python must be converted to use one of the above fns. -->

::::::::::::::::::::::::::::::::::::: callout

The built-in functions [`filter()`](https://docs.python.org/3/library/functions.html#filter) and [`map()`](https://docs.python.org/3/library/functions.html#map) can be used for processing iterables. However list-comprehension is likely to be more performant.

<!-- Would this benefit from an example? -->

:::::::::::::::::::::::::::::::::::::::::::::

This is a nice illustration of the principle we discussed earlier:
It is often best to tell the interpreter/library at a high level *what you want*, and let it figure out *how to do it*.


## Example: Searching an element in a list

A simple example of this would be to perform a linear search of a list. (Though as we’ll see in the next section, there’s a much more effective way to do this!)
The below example creates a list of 2500 integers in the inclusive-exclusive range `[0, 5000)`.
It then searches for all of the even numbers in that range.
`manualSearch()` is implemented manually, iterating `ls` checking each individual item in Python code.
`operatorSearch()` in contrast uses the `in` keyword to perform each search, which allows CPython to implement the inner loop in its C back-end.

```python
import random

N = 2500  # Number of elements in list
M = 2  # N*M == Range over which the elements span

def generateInputs():
    random.seed(12)  # Ensure every list is the same
    return [random.randint(0, int(N*M)) for i in range(N)]
    
def manualSearch():
    ls = generateInputs()
    ct = 0
    for i in range(0, int(N*M), M):
        for j in range(0, len(ls)):
            if ls[j] == i:
                ct += 1
                break

def operatorSearch():
    ls = generateInputs()
    ct = 0
    for i in range(0, int(N*M), M):
        if i in ls:
            ct += 1

repeats = 1000
gen_time = timeit(generateInputs, number=repeats)
print(f"manualSearch: {timeit(manualSearch, number=repeats)-gen_time:.2f}ms")
print(f"operatorSearch: {timeit(operatorSearch, number=repeats)-gen_time:.2f}ms")
```

This results in the manual Python implementation being 5x slower, doing the exact same operation!

```output
manualSearch: 152.15ms
operatorSearch: 28.43ms
```

An easy approach to follow is that if two blocks of code do the same operation, the one that contains less Python is probably faster. This won't apply if you're using 3rd party packages written purely in Python though.

::::::::::::::::::::::::::::::::::::: callout

### Python bytecode


You can use `dis` to view the bytecode generated by Python, the amount of byte-code more strongly correlates with how much code is being executed by the Python interpreter. However, this still does not account for whether functions called are implemented using Python or C.

The pure Python search compiles to 82 lines of byte-code.

```python
import dis

def manualSearch():
    ls = generateInputs()
    ct = 0
    for i in range(0, int(N*M), M):
        for j in range(0, len(ls)):
            if ls[j] == i:
                ct += 1
                break

dis.dis(manualSearch)
```
```output
 11           0 LOAD_GLOBAL              0 (generateInputs)
              2 CALL_FUNCTION            0
              4 STORE_FAST               0 (ls)

 12           6 LOAD_CONST               1 (0)
              8 STORE_FAST               1 (ct)

 13          10 LOAD_GLOBAL              1 (range)
             12 LOAD_CONST               1 (0)
             14 LOAD_GLOBAL              2 (int)
             16 LOAD_GLOBAL              3 (N)
             18 LOAD_GLOBAL              4 (M)
             20 BINARY_MULTIPLY
             22 CALL_FUNCTION            1
             24 LOAD_GLOBAL              4 (M)
             26 CALL_FUNCTION            3
             28 GET_ITER
        >>   30 FOR_ITER                24 (to 80)
             32 STORE_FAST               2 (i)

 14          34 LOAD_GLOBAL              1 (range)
             36 LOAD_CONST               1 (0)
             38 LOAD_GLOBAL              5 (len)
             40 LOAD_FAST                0 (ls)
             42 CALL_FUNCTION            1
             44 CALL_FUNCTION            2
             46 GET_ITER
        >>   48 FOR_ITER                14 (to 78)
             50 STORE_FAST               3 (j)

 15          52 LOAD_FAST                0 (ls)
             54 LOAD_FAST                3 (j)
             56 BINARY_SUBSCR
             58 LOAD_FAST                2 (i)
             60 COMPARE_OP               2 (==)
             62 POP_JUMP_IF_FALSE       38 (to 76)

 16          64 LOAD_FAST                1 (ct)
             66 LOAD_CONST               2 (1)
             68 INPLACE_ADD
             70 STORE_FAST               1 (ct)

 17          72 POP_TOP
             74 JUMP_FORWARD             1 (to 78)

 15     >>   76 JUMP_ABSOLUTE           24 (to 48)
        >>   78 JUMP_ABSOLUTE           15 (to 30)

 13     >>   80 LOAD_CONST               0 (None)
             82 RETURN_VALUE
```

Whereas the `in` variant only compiles to 54.

```python
import dis

def operatorSearch():
    ls = generateInputs()
    ct = 0
    for i in range(0, int(N*M), M):
        if i in ls:
            ct += 1

dis.dis(operatorSearch)
```
```output
  4           0 LOAD_GLOBAL              0 (generateInputs)
              2 CALL_FUNCTION            0
              4 STORE_FAST               0 (ls)

  5           6 LOAD_CONST               1 (0)
              8 STORE_FAST               1 (ct)

  6          10 LOAD_GLOBAL              1 (range)
             12 LOAD_CONST               1 (0)
             14 LOAD_GLOBAL              2 (int)
             16 LOAD_GLOBAL              3 (N)
             18 LOAD_GLOBAL              4 (M)
             20 BINARY_MULTIPLY
             22 CALL_FUNCTION            1
             24 LOAD_GLOBAL              4 (M)
             26 CALL_FUNCTION            3
             28 GET_ITER
        >>   30 FOR_ITER                10 (to 52)
             32 STORE_FAST               2 (i)

  7          34 LOAD_FAST                2 (i)
             36 LOAD_FAST                0 (ls)
             38 CONTAINS_OP              0
             40 POP_JUMP_IF_FALSE       25 (to 50)

  8          42 LOAD_FAST                1 (ct)
             44 LOAD_CONST               2 (1)
             46 INPLACE_ADD
             48 STORE_FAST               1 (ct)
        >>   50 JUMP_ABSOLUTE           15 (to 30)

  6     >>   52 LOAD_CONST               0 (None)
             54 RETURN_VALUE
```

:::::::::::::::::::::::::::::::::::::::::::::


## Example: Parsing data from a text file

In C, since there is no high-level `string` datatype, parsing strings can be fairly arduous work where you repeatedly look for the index of a separator character in the string and use that index to split the string up.


::::::::::::::::::::::::::::::::::::: challenge

Let’s say we have read in some data from a text file, each line containing a time bin and a mean energy:

```python
f = [
    ' 0000   0.9819 ',
    ' 0001   0.3435 ',
    # ...
    ' 0099   0.2275 ',
    ' 0100   0.7067 ',
    # ...
]
```

If you've a C programming background, you may write the following code to parse the data into a dictionary:
```python
def manualSplit():
    data = {}
    for line in f:
        first_char = line.find("0")
        end_time = line.find(" ", first_char, -1)

        energy_found = line.find(".", end_time, -1)
        begin_energy = line.rfind(" ", end_time, energy_found)
        end_energy = line.find(" ", energy_found)
        if end_energy == -1:
            end_energy = len(line)
        
        time = line[first_char:end_time]
        energy = line[begin_energy + 1:end_energy]

        data[time] = energy
    return data
```

Can you find a shorter, more easily understandable way to write this in Python?

:::::::::::::::::::::::: hint

Python strings have a lot of methods to perform common operations, like removing suffixes, replacing substrings, joining or splitting, stripping whitespaces, and much more. See Python's [string methods documentation](https://docs.python.org/3/library/stdtypes.html#string-methods) for a full list.

:::::::::::::::::::::::::::::::::

:::::::::::::::::::::::: solution

```python

def builtinSplit():
    data = {}
    for line in f:
        time, energy = line.split()
        data[time] = energy
    return data
```

This code is not just much more readable; it is also more flexible, since it does not rely on the precise formatting of the input strings.
(For example, the line `first_char = line.find("0")` in the original code assumes that the time bin starts with the digit 0. That code would likely malfunction if the input file had more than 1000 time bins.)

The code that’s executed by CPython may use a similar approach as in `manualSplit()`; however, since this is all happening "under the hood" in C code, it is once again faster.

```python

N = 10_000  # Number of elements in the list

# Ensure every list is the same
random.seed(12)
f = [f" {i:0>6d} {random.random():8.4f} " for i in range(N)]

repeats = 1000
print(f"manualSplit: {timeit(manualSplit, globals=globals(), number=repeats):.3f}ms")
print(f"builtinSplit: {timeit(builtinSplit, globals=globals(), number=repeats):.3f}ms")
```

```output
manualSplit: 1.797ms
builtinSplit: 0.796ms
```

:::::::::::::::::::::::::::::::::
:::::::::::::::::::::::::::::::::::::::::::::::


::::::::::::::::::::::::::::::::::::: challenge

If you’ve brought a project you want to work on: Do you have any similar code in there, which is hard to understand because it contains a lot of low-level step-by-step instructions?

:::::::::::::::::::::::: hint

<!-- Typical cases might include reading data from a file, …, … TODO: more examples? -->

(Before you try to rewrite those parts of your code, use a profiler to see whether those parts have a noticeable impact on the overall performance of your project. Remember the Donald Knuth quote!)

:::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::::::::
