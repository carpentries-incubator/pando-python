---
title: "Keep Python & Packages up to Date"
teaching: 10
exercises: 0
---

:::::::::::::::::::::::::::::::::::::: questions

- Why would a newer version of Python or a package be faster?
- Are there any risks to updating Python and packages?
- How can reproducibility be ensured through package upgrades?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

- Able to explain why using the latest versions of Python and packages is beneficial.
- Able to identify when updating is not possible due to incompatibilities. 
- Able to ensure code remains reproducible through package changes.

::::::::::::::::::::::::::::::::::::::::::::::::

## Introduction

<!-- Why it's important to use the most recent Python and packages viable -->
It's important to use the latest Python wherever feasible. In addition to new features and fixes, much work has been completed over the lifetime of Python 3 to improve the performance of the language.

> [Python 3.11](https://docs.python.org/3/whatsnew/3.11.html) is between 10-60% faster than Python 3.10. On average, we measured a 1.25x speedup on the standard benchmark suite.

Future proposals, such as changes to the [JIT](https://tonybaloney.github.io/posts/python-gets-a-jit.html) and [GIL](https://peps.python.org/pep-0703/) will provide further improvements to performance.

Similarly, major packages with a performance focus such as NumPy and Pandas, should be kept up to date for the same reasons.

<!-- performance regressions for major packages are rare -->
These improvements are often free, requiring minimal changes to any code (unlike the jump from Python 2 to Python 3).

Performance regressions within major packages should be considered rare, they often track performance alongside their test suites.

::::::::::::::::::::::::::::::::::::: callout

## Support for older Python versions in the Scientific Python ecosystem

In the last few years, many important packages in the Scientific Python ecosystem have agreed [a common policy](https://scientific-python.org/specs/spec-0000/) to support previous versions of Python for 3 years.
For example, since October 2024, these packages stopped supporting Python 3.10; so if you are still using Python 3.10 (or even older versions), you’re now losing access to new features and performance improvements in NumPy, SciPy, Matplotlib and many other libraries. Time to update!

:::::::::::::::::::::::::::::::::::::


<!-- Not always possible due to incompatibilities -->
However, the more packages and language features your code touches, and the older the Python it currently uses, the greater chance of incompatibilities making it difficult to upgrade.

<!-- Updates may include breaking changes, important to have validation inplace to ensure results aren't affected -->
Similar to optimising, when updating it's important to have tests in place to validate the correctness of your code before and after changes.
An update to a single small dependent package could introduce a breaking change.
This could cause your code to crash, or worse subtly change your results.


## Updating Python & Packages

<!-- Not as relevant if you are starting from scratch -->
*This isn't as relevant if you're starting from scratch. Simply make sure you've installed the latest Python before you start.*


<!-- todo recommended way, because Python is incredibly bad at this -->
If you have been working with an existing Python installation, the upgrade process for Python itself depends on how you installed your current version. (E.g. via conda, official installer from python.org, package manager like Homebrew/apt/yum/…)

For packages you’re using, you can update those with the same package manager you used to installed them:

* via `pip`, e.g. `pip install --upgrade numpy`
* via `conda`, e.g. `conda update <PACKAGE>`

<!-- Worth also mentioning for same reason, to have requirements.txt? -->



::::::::::::::::::::::::::::::::::::: keypoints

- Where feasible, the latest version of Python and packages should be used as they can include significant free improvements to the performance of your code.
- There is a risk that updating Python or packages will not be possible to due to version incompatibilities or will require breaking changes to your code.
- Changes to packages may impact results output by your code, ensure you have a method of validation ready prior to attempting upgrades.

::::::::::::::::::::::::::::::::::::::::::::::::
