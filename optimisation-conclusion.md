---
title: "Optimisation Conclusion"
teaching: 5
exercises: 0
---

:::::::::::::::::::::::::::::::::::::: questions

- What has been learnt about writing performant Python?

::::::::::::::::::::::::::::::::::::::::::::::::


::::::::::::::::::::::::::::::::::::: objectives

- Review what has been learnt about writing performant Python

::::::::::::::::::::::::::::::::::::::::::::::::

This concludes the optimisation portion of the course.

An overview of how Python operates and the most important practices for achieving performant code have been introduced.

Hopefully with the information from this course you will be in a better position to investigate and optimise the performance of your own code.

This course's website can be used as a reference manual when profiling your own code.
<!--
::::::::::::::::::::::::::::::::::::: callout

## Your Feedback is Required!

Please complete [this Google form](https://forms.gle/C82uWBEou3FMrQs99) to let us know what you think we've missed.

Your feedback enables us to improve the course for future attendees!

:::::::::::::::::::::::::::::::::::::::::::::
-->

::::::::::::::::::::::::::::::::::::: keypoints

- Using Python Language Features and the Standard Library
    - Python is an interpreted language. This adds an additional overhead at runtime to the execution of Python code. Many core Python functions are implemented in faster C/C++, free from this overhead.
    - Where possible, use built-in functions (like `sum()`, `min()` or `max()`), language features (like list comprehensions) and standard library functionality (like `str.split()`) instead of re-inventing the wheel. This makes your code more readable and is often more performant.
- Data Structures & Algorithms
    - List comprehension should be preferred when constructing lists.
    - Where appropriate, Tuples and Generator functions should be preferred over Python lists.
    - Dictionaries and sets are appropriate for storing a collection of unique data with no intrinsic order for random access.
    - When used appropriately, dictionaries and sets are significantly faster than lists.
    - If searching a list or array is required, it should be sorted and searched using `bisect_left()` (binary search).
- Minimise Python Written
    - Like many core Python functions, NumPy functions are implemented in faster C/C++.
    - Additionally, NumPy can take advantage of vectorisation to process arrays, which can greatly improve performance.
    - Pandas' data tables store columns as arrays, therefore operations applied to columns can take advantage of NumPys vectorisation.
- Newer is Often Faster
    - Where feasible, the latest version of Python and packages should be used as they can include significant free improvements to the performance of your code.
    - There is a risk that updating Python or packages will not be possible to due to version incompatibilities or will require breaking changes to your code.
    - Changes to packages may impact results output by your code, ensure you have a method of validation ready prior to attempting upgrades.
- How Latency Affects Performance
    - One large file is preferable to many small files.
    - Network requests can be parallelised to reduce the impact of fixed overheads.
    - Memory allocation is not free, avoiding destroying and recreating objects can improve performance.

::::::::::::::::::::::::::::::::::::::::::::::::
