---
title: "Profiling Conclusion"
teaching: 5
exercises: 0
---

:::::::::::::::::::::::::::::::::::::: questions

- What has been learnt about profiling?

::::::::::::::::::::::::::::::::::::::::::::::::


::::::::::::::::::::::::::::::::::::: objectives

- Review what has been learnt about profiling

::::::::::::::::::::::::::::::::::::::::::::::::

This concludes the profiling portion of the course.

`cProfile`, `snakeviz` and `line_profiler` have been introduced, these are some of the most accessible Python profiling tools.

With these transferable skills, if necessary, you should be able to follow documentation to use more advanced Python profiling tools such as [`scalene`](https://github.com/plasma-umass/scalene).

::::::::::::::::::::::::::::::::::::: keypoints

What profiling is:

- The collection and analysis of metrics relating to the performance of a program during execution .

Why programmers can benefit from profiling:

- Narrows down the costly areas of code, allowing optimisation to be prioritised or decided to be unnecessary.

When to Profile:

- Profiling should be performed on functional code, either when concerned about performance or prior to release/deployment.

What to Profile:

- The collection of profiling metrics will often slow the execution of code, therefore the test-case should be narrow whilst remaining representative of a realistic run.

How to function-level profile:

- Execute `cProfile` via `python -m cProfile -o <output file> <script name> <arguments>`
- Execute `snakeviz` via `python -m snakeviz <output file>`

How to line-level profile:

- Import `profile` from `line_profiling`
- Decorate targeted functions with `@profile`
- Execute `line_profiler` via `python -m kernprof -lvr <script name> <arguments>`

::::::::::::::::::::::::::::::::::::::::::::::::
