---
title: Acknowledgements
---

**Funding**

The development of this course was funded by the [University of Sheffield](https://www.sheffield.ac.uk) to support researchers working with their [Stanage](https://docs.hpc.shef.ac.uk/en/latest/stanage/index.html#gsc.tab=0) HPC system.

**Authorship**

The initial materials were authored by [Robert Chisholm](https://www.sheffield.ac.uk/dcs/people/research-staff/robert-chisholm), with support from various colleagues within the University of Sheffield's [Research Software Engineering](https://rse.shef.ac.uk) and [Research IT](https://www.sheffield.ac.uk/it-services/research) teams.
Additional consulting was provided by James Kilbane, a close friend (and general rubber duck).

[Jost Migenda](https://www.kcl.ac.uk/people/jost-migenda) from the [KCL e-Research department](https://www.kcl.ac.uk/research/facilities/e-research) contributed significant improvements and additions to the optimization episodes. They have also become a co-maintainer of the course.

Anastasiia Shcherbakova and Mira Sarkis of [ICR-RSE](https://github.com/ICR-RSE-Group) contributed inspiration for the list append figure and a large number of typographic corrections and simplifications during the alpha phase of the course's development lifecycle.

**Resources**

Most of the content was drawn from the education and experience of the authors, however the below resources provided inspiration:

* [High Performance Python, 2nd Edition](https://www.oreilly.com/library/view/high-performance-python/9781492055013/): This excellent book goes far deeper than this short course in explaining how to maximise performance in Python, however it inspired the examples; [memory allocation is not free](optimisation-latency.html#memory-allocation-is-not-free) and [vectorisation](optimisation-latency.html#memory-allocation-is-not-free).
* [What scientists must know about hardware to write fast code](https://viralinstruction.com/posts/hardware/): This notebook provides an array of hardware lessons relevant to programming for performance, which could be similarly found in most undergraduate Computer Science courses. Although the notebook is grounded in Julia, a lower level language than Python, it is referring to hardware so many of same lessons are covered in the [latency episode](optimisation-latency).
* [Why Python is Slow: Looking Under the Hood](https://jakevdp.github.io/blog/2014/05/09/why-python-is-slow/): This blog post looks under the hood of CPython to explain why Python is often slower than C (and NumPy). We reproduced two of its figures in the [optimisation introduction](optimisation-introduction.html) and [numpy](optimisation-numpy) episodes to explain how memory is laid out.
