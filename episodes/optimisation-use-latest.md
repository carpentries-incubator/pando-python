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
It's important to use the latest Python version wherever feasible. In addition to new features and fixes, much work has been completed over the lifetime of Python 3 to improve the performance of the language. On average, [Python 3.11](https://docs.python.org/3/whatsnew/3.11.html) was about 25% faster than Python 3.10; since then, Python 3.12 to 3.14 have each introduced additional speedups. Overall, average performance has improved [by about 50%](https://www.youtube.com/watch?v=NE-Oq8I3X_w&t=2m22s) in those four years.

Future proposals, such as changes to the [JIT](https://tonybaloney.github.io/posts/python-gets-a-jit.html) and [GIL](https://peps.python.org/pep-0703/) will provide further improvements to performance.

Similarly, major packages with a performance focus, such as NumPy and Pandas, should be kept up to date for the same reasons.

Performance regressions in Python itself or in those packages are fairly rare, since they often track performance alongside their test suites.

::::::::::::::::::::::::::::::::::::: callout

## Support for older Python versions in the Scientific Python ecosystem

In the last few years, many important packages in the Scientific Python ecosystem have agreed [a common policy](https://scientific-python.org/specs/spec-0000/) to support previous versions of Python for 3 years.
For example, since October 2024, these packages stopped supporting Python 3.10; so if you are still using Python 3.10 (or even older versions), you’re now losing access to new features and performance improvements in NumPy, SciPy, Matplotlib and many other libraries. Time to update!

:::::::::::::::::::::::::::::::::::::


<!-- Not always possible due to incompatibilities -->
These improvements are often free, requiring minimal changes to any code (unlike the jump from Python 2 to Python 3).
However, the more packages and language features your code touches, and the older the Python version it currently uses, the greater the risk of incompatibilities that require some work to upgrade.

<!-- Updates may include breaking changes, important to have validation inplace to ensure results aren't affected -->
As with other optimisations, when updating it's important to have tests in place to validate the correctness of your code before and after changes.
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
