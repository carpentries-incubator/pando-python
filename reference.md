---
title: 'Reference'
---

## Glossary

Array
: A data-structure that stores a collection of elements, typically of the same type, arranged in contiguous memory locations. Arrays enable elements to be iterated in order or directly accessed according to their index. Arrays do not support appending or removing items, Python's lists wrap an array to provide support for greater flexibility such as appending.

Benchmarking
: The process of running a program in order to assess its overall performance. This can be useful to confirm the impact of optimisations.

Bottleneck
: The component with the lowest throughput, which limits performance of the overall program. Improving the throughput of this component should improve the overall performance.

*Bottleneck is a synonym of limiting factor.*

Call Stack
: The internal stack data-structure used during the execution of code, that tracks metadata related to the currently executing hierarchy of function calls. Elements in the call stack are referred to as stack frames.

`cProfile`
: A function level profiler provided by the Python standard library.

Hot Path
: The parts of the code that are executed very frequently during normal operation.

Latency
: The time taken for an operation to complete.

Limiting Factor
: The component with the lowest throughput, which limits performance of the overall program. Improving the throughput of this component should improve the overall performance.

*Limiting factor is a synonym of bottleneck.*

`line_profiler`
: A line level profiler for Python that can be installed via `pip`.

Pop
: The action of removing the top item from a stack data-structure (sometimes also used in reference to removing and returning the first item from a list or queue).

Profiling
: The measuring and analysis of granular performance metrics of a program, to understand where time is being spent during execution. Typically used to prioritise optimisation.

Push
: The action of adding an item to the top of a stack data-structure (sometimes also used in reference to appending an item to a list or queue).

Recursive
: A recursive function or algorithm is one that calls itself. Too many recursive calls, can lead to stack overflow exceptions. Most recursive functions can be restructured as loops.

`snakeviz`
: A web-browser based visualisation tool for `cProfile` outputs that can be installed via `pip`.

Stack
: A last-in-first-out (LIFO) data structure. Similar in nature to a physical stack (e.g. of books), items are added to the top and those below the top cannot be accessed without first removing the ones above them.

Stack Frame
: The term used to refer to elements within the call stack. A call stack's stack frame will contain metadata about a particular function call, such as where it was called from and any variables that have been allocated 'on the stack' within the function's local scope. When a stack frame is popped from the call stack, any variables allocated within the corresponding function's local scope would be deallocated.

`viztracer`
: A timeline profiler for Python that can be installed via `pip`.
