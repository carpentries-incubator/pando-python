---
site: sandpaper::sandpaper_site
---

<!--
![Welcome to Performance Profiling & Optimisation (Python) Training!
](episodes/fig/pando-python-hex-sticker.png){
alt='Performance Profiling & Optimisation (Python) Training'
style='padding: 2%'}
-->

**Welcome to Performance Profiling & Optimisation (Python) Training!**

The training curriculum for this course is designed for researchers that are writing Python and lack formal computer science training. The curriculum covers how to assess where time is being spent during execution of a Python program, it also provides a high level understanding of how code executes and how this maps to the limiting factors of performance and good practice.

If you are now comfortable using Python, this course may be of interest to supplement and advance your programming knowledge. This course is particularly relevant if you are writing research code and desire greater confidence that your code is both performant and suitable for publication.

This is an all-day course, however it normally finishes by early afternoon.

<!-- TODO: course duration? -->
<!-- TODO: confident code syllabus? -->

## Motivation

Why might you want to profile and optimise your code?

The simplest answer is that optimisation let you get results faster. It may also allow you to scale up your code to perform larger analyses that would otherwise have taken too long to be practical.

Making your code faster can have additional benefits: faster software uses less compute power. If you use paid-for compute resources, such as cloud computing or some HPC facilities, optimising your code can therefore reduce your costs.

Using less computing power also helps make your software more environmentally sustainable. As funders and research institutions set Net Zero goals, and computationally-intensive research expands, sustainability is increasingly becoming a concern for researchers.

::::::::::::::::::::::::::::::::::::: callout

### Green computing

To find out more about sustainable computing, visit the [Green DiSC](https://www.software.ac.uk/GreenDiSC) website or see this [online training](https://learn.greensoftware.foundation/) from the Green Software Foundation.

:::::::::::::::::::::::::::::::::::::

However, it's sensible to focus your optimisation efforts on the parts of the code that take the longest. This is where profiling comes in: by profiling your code, you can identify which parts contribute the most to its runtime, and target these for optimisation.
Even if you don’t find any major performance gains, profiling can give you a better understanding of what your code is doing, or give you confidence that the performance of your code matches your expectations.

## Learning Objectives
<!-- Aim for 3-4 objectives for every 6 hours of training -->
<!-- SMART Objectives
    - Specific
    - Measurable
    - Attainable (within the span of the course)
    - Relevant
    - Time-bound (implicitly the length of the course)
-->
<!-- Evaluation tool: https://web.cs.manchester.ac.uk/iloadvisor/ -->
After attending this training, participants will be able to:

- identify the most expensive functions and lines of code using `cprofile` and `line_profiler`.
- evaluate code to determine the limiting factors of its performance.
- recognise and implement optimisations for common limiting factors of performance.

::::::::::::::::::::::::::::::::::::::::::  prereq

## Prerequisites

Before joining Performance Profiling & Optimisation (Python) Training, participants should be able to:

- implement basic algorithms in Python.
- follow the control flow of Python code, and dry run the execution in their head or on paper.

See Software Carpentry's [Python novice course](https://swcarpentry.github.io/python-novice-inflammation/) for help with learning these skills.

<!-- TODO: could make a dedicated page (like https://carpentries.github.io/lesson-development-training/markdown-github-primer.html) that highlights specific courses/resources. -->

::::::::::::::::::::::::::::::::::::::::::::::::::
