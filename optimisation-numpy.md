---
title: "Using Scientific Python Packages (NumPy, Pandas and more)"
teaching: 30
exercises: 0
---

:::::::::::::::::::::::::::::::::::::: questions

- Why is NumPy often faster than raw Python?
- How can processing rows of a Pandas data table be made faster?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

- Able to utilise NumPy's vectorisation when operating on arrays of data.
- Able to efficiently process rows when working with data tables.

::::::::::::::::::::::::::::::::::::::::::::::::

Earlier, we saw that built-in Python functions, like `sum()`, are often faster than manually looping over a list. This is because those high-level functions are able to do most of the work in the C backend.

Packages like NumPy and Pandas work similarly: They have been written in compiled languages to expose this performance across a wide range of scientific workloads.



## Using NumPy (Effectively)

[NumPy](https://numpy.org/) is a commonly used package for scientific computing, which provides a wide variety of methods.

It adds restriction via its own [basic numeric types](https://numpy.org/doc/stable/user/basics.types.html) and static arrays to enable even greater performance than that of core Python. However if these restrictions are ignored, the performance can become significantly worse.

![Illustration of a NumPy array and a Python list.](episodes/fig/numpy-array-vs-list.png){alt="A diagram illustrating the difference between a NumPy array and a Python list. The NumPy array is a raw block of memory containing numerical values. A Python list contains a header with metadata and multiple items, each of which is a reference to another Python object with its own header and value."}
<!-- Figure inspired by https://jakevdp.github.io/blog/2014/05/09/why-python-is-slow/#3.-Python's-object-model-can-lead-to-inefficient-memory-access -->

### NumPy Arrays and Python Lists Live in Two Separate Worlds

NumPy's arrays (not to be confused with the core Python `array` package) are static arrays. Unlike core Python's lists, they do not dynamically resize. Therefore, if you wish to append to a NumPy array, you must call `resize()` first. If you treat this like `append()` for a Python list, resizing for each individual append, you will be performing significantly more copies and memory allocations than a Python list.

The below example sees lists and arrays constructed from `range(100000)`.

```python
from timeit import timeit
import numpy

N = 100000  # Number of elements in list/array

def list_append():
    ls = []
    for i in range(N):
        ls.append(i)

def array_resize():
    ar = numpy.zeros(1)
    for i in range(1, N):
        ar.resize(i+1)
        ar[i] = i
        
repeats = 1000
print(f"list_append: {timeit(list_append, number=repeats):.2f}ms")
print(f"array_resize: {timeit(array_resize, number=repeats):.2f}ms")
```

For Python lists, we've seen earlier that list comprehensions are more efficient, so we prefer to avoid using a large number of `append` operations if possible. Similarly, we should try to avoid resizing NumPy arrays, where the overhead is even higher (5.2x slower than a list, probably 10x slower than list comprehension).

```output
list_append: 3.50ms
array_resize: 18.04ms
```

Another difference, is that NumPy arrays typically require all data to be the same type (and a NumPy type). This enables more efficient access to elements, as they all exist contiguously in memory. In contrast, elements within Python lists can be of any type so the list always stores a pointer to where the element actually exists in memory, rather than the actual element. This has the side effect that if you are converting back and forth between Python lists and NumPy arrays, there is an additional overhead as it's not as simple as copying a single block of memory.

::::::::::::::::::::::::::::::::::::: callout

If you construct a NumPy array from a list containing a complex object, it will store your data as Python types and you won't be able to take advantage of NumPy's optimisations.

```sh
>python
>>> import numpy as np
>>> a = np.array([0.5, 5])
>>> type(a[0])
<class 'numpy.float64'>
>>> type(a[1])
<class 'numpy.float64'>
>>> b = np.array([0.5, 5,{"foo":5}])
>>> type(b[0])
<class 'float'>
>>> type(b[1])
<class 'int'>
>>> type(b[2])
<class 'dict'>
```

:::::::::::::::::::::::::::::::::::::::::::::

The below example demonstrates the overhead of mixing Python lists and NumPy functions.

```sh
# Python list, numpy.random.choice()
>python -m timeit -s "import numpy; ls = list(range(10000))" "numpy.random.choice(ls)"
1000 loops, best of 5: 267 usec per loop

# NumPy array, numpy.random.choice()
>python -m timeit -s "import numpy; ar = numpy.arange(10000)" "numpy.random.choice(ar)"
50000 loops, best of 5: 4.06 usec per loop
```

Passing a Python list to `numpy.random.choice()` is 65.6x slower than passing a NumPy array. This is the additional overhead of converting the list to an array. If this function were called multiple times, it would make sense to transform the list to an array before calling the function so that overhead is only paid once.

::::::::::::::::::::::::::::::::::::: callout

```sh
# Python list, Manually select 1 item
>python -m timeit -s "import numpy; ls = list(range(10000))" "ls[numpy.random.randint(len(ls))]"
200000 loops, best of 5: 1.19 usec per loop

# NumPy array, Manually select 1 item
>python -m timeit -s "import numpy; ar = numpy.arange(10000)" "ar[numpy.random.randint(len(ar))]"
200000 loops, best of 5: 1.22 usec per loop
```

Regardless, for this simple application of `numpy.random.choice()`, merely using `numpy.random.randint(len())` is around 4x faster regardless whether a Python list or NumPy array is used. 

With `numpy.random.choice()` being such a general function (it has many possible parameters), there is significant internal branching. If you don't require this advanced functionality and are calling a function regularly, it can be worthwhile considering using a more limited function.

There is however a trade-off, using `numpy.random.choice()` can be clearer to someone reading your code, and is more difficult to use incorrectly.

:::::::::::::::::::::::::::::::::::::::::::::

### Array Broadcasting

NumPy arrays support "[broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html)" many mathematical operations or functions.
This is a shorthand notation, where the operation/function is applied element-wise without having to loop over the array explicitly:

```Python
>>> import numpy as np
>>> ar = np.arange(6)
>>> ar
array([0, 1, 2, 3, 4, 5])
>>> ar + 10
array([10, 11, 12, 13, 14, 15])
>>> ar * 2
array([ 0,  2,  4,  6,  8, 10])
>>> ar**2
array([ 0,  1,  4,  9, 16, 25])
>>> np.exp(ar)
array([  1.        ,   2.71828183,   7.3890561 ,  20.08553692,
        54.59815003, 148.4131591 ])
```

::::::::::::::::::::::::::::::::::::: callout

If you try the same with Python lists, it will usually fail with an error or give an unexpected result:

```Python
>>> ls = list(range(6))
>>> ls + 10
Traceback (most recent call last):
  File "<python-input-8>", line 1, in <module>
    ls + 10
    ~~~^~~~
TypeError: can only concatenate list (not "int") to list
>>> ls * 2
[0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5]
>>> ls ** 2
Traceback (most recent call last):
  File "<python-input-10>", line 1, in <module>
    ls ** 2
    ~~~^^~~
TypeError: unsupported operand type(s) for ** or pow(): 'list' and 'int'
>>> np.exp(ls)  # works but is slower, because NumPy converts the list into an array first
array([  1.        ,   2.71828183,   7.3890561 ,  20.08553692,
        54.59815003, 148.4131591 ])
```
:::::::::::::::::::::::::::::::::::::::::::::

However, broadcasting is not just a nicer way to write mathematical expressions—it can also give a significant performance boost:
Most modern processors are able to apply one instruction across multiple variables simultaneously, instead of sequentially. (In computer science, this is also referred to as "vectorisation".) The manner by which NumPy stores data in arrays enables it to vectorise mathematical operations that are broadcast across arrays.


```sh
> python -m timeit -s "import numpy; ar = numpy.arange(1)" "ar + 10"
1000000 loops, best of 5: 359 nsec per loop
> python -m timeit -s "import numpy; ar = numpy.arange(10)" "ar + 10"
1000000 loops, best of 5: 362 nsec per loop
> python -m timeit -s "import numpy; ar = numpy.arange(100)" "ar + 10"
1000000 loops, best of 5: 364 nsec per loop
```
If we were to use a regular `for` loop, the time to perform this operation would increase with the length of the array.
However, using NumPy broadcasting we can apply the addition to 1, 10 or 100 elements, all in the same amount of time!

::::::::::::::::::::::::::::::::::::: instructor

A simple analogy:

If you're baking cookies, the oven (CPU register) is big enough to operate on multiple cookies (numbers) simultaneously. So whether you bake 1 cookie or 10, it'll take exactly the same amount of time.
However, this requires that the cookies are neatly arranged on a baking tray (in a contiguous chunk of memory).

Basic ints/floats in NumPy arrays are arranged like that, so this works great.
In contrast, numbers in a Python list [are spread across memory in a fairly complex arrangement](https://jakevdp.github.io/blog/2014/05/09/why-python-is-slow/#3.-Python's-object-model-can-lead-to-inefficient-memory-access), so cannot benefit from this unless you convert them to a NumPy array first.

::::::::::::::::::::::::::::::::::::::::::::::::

Earlier it was demonstrated that using core Python methods over a list will outperform a loop, performing the same calculation faster. The below example takes this a step further by demonstrating the calculation of a dot product.

<!-- Inspired by High Performance Python Chapter 6 example 
Added Python sum array, skipped a couple of others--> 
```python
from timeit import timeit

N = 1000000  # Number of elements in list

gen_list = f"ls = list(range({N}))"
gen_array = f"import numpy; ar = numpy.arange({N}, dtype=numpy.int64)"

py_sum_ls = "sum([i*i for i in ls])"
py_sum_ar = "sum(ar*ar)"
np_sum_ar = "numpy.sum(ar*ar)"
np_dot_ar = "numpy.dot(ar, ar)"

repeats = 1000
print(f"python_sum_list: {timeit(py_sum_ls, setup=gen_list, number=repeats):.2f}ms")
print(f"python_sum_array: {timeit(py_sum_ar, setup=gen_array, number=repeats):.2f}ms")
print(f"numpy_sum_array: {timeit(np_sum_ar, setup=gen_array, number=repeats):.2f}ms")
print(f"numpy_dot_array: {timeit(np_dot_ar, setup=gen_array, number=repeats):.2f}ms")
```

```output
python_sum_list: 46.93ms
python_sum_array: 33.26ms
numpy_sum_array: 1.44ms
numpy_dot_array: 0.29ms
```

* `python_sum_list` uses list comprehension to perform the multiplication, followed by the Python core `sum()`. This comes out at 46.93ms
* `python_sum_array` instead directly multiplies the two arrays (taking advantage of NumPy's vectorisation) but uses the core Python `sum()`, this comes in slightly faster at 33.26ms.
* `numpy_sum_array` again takes advantage of NumPy's vectorisation for the multiplication, and additionally uses NumPy's `sum()` implementation. These two rounds of vectorisation provide a much faster 1.44ms completion.
* `numpy_dot_array` instead uses NumPy's `dot()` to calculate the dot product in a single operation. This comes out the fastest at 0.29ms, 162x faster than `python_sum_list`. 


::::::::::::::::::::::::::::::::::::: callout

## Parallel NumPy

<!-- https://superfastpython.com/multithreaded-numpy-functions/ -->
NumPy can sometimes take advantage of auto parallelisation, particularly on HPC systems.

A small number of functions are backed by BLAS and LAPACK, enabling even greater speedup.

The [supported functions](https://numpy.org/doc/stable/reference/routines.linalg.html) mostly correspond to linear algebra operations like `numpy.dot()`.

The auto-parallelisation of these functions is hardware-dependent, so you won't always automatically get the additional benefit of parallelisation.
However, HPC systems should be primed to take advantage, so try increasing the number of cores you request when submitting your jobs and see if it improves the performance.

*This might be why `numpy_dot_array` is that much faster than `numpy_sum_array` in the previous example!*

:::::::::::::::::::::::::::::::::::::


## Other Libraries That Use NumPy

Across the scientific Python software ecosystem, [many domain-specific packages](https://numpy.org/#:~:text=ECOSYSTEM) are built on top of NumPy arrays.
Similar to the demos above, we can often gain significant performance boosts by using these libraries well.

::::::::::::::::::::::::::::::::::::: challenge

### Challenge: Which Libraries Are You Using Already?

Take a look at the [list of libraries on the NumPy website](https://numpy.org/#:~:text=ECOSYSTEM). Are you using any of them already?

If you've brought a project you want to work on: Are there areas of the project where you might benefit from adapting one of these libraries instead of writing your own code from scratch?

:::::::::::::::::::::::: hint

These libraries could be specific to your area of research; but they could also include packages from other fields that provide tools you need (e.g. statistics or machine learning)!

:::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::::::::


Which libraries you may use will depend on your research domain; here, we'll show an example from bioinformatics.

### Example: Image Analysis with Shapely

A bioinformatics researcher had a large data set of images of cells. She had already reconstructed the locations of cell walls and various points of interest and needed to identify which points were located in each cell.
To do this, she used the [Shapely](https://github.com/shapely/shapely) geometry library.

```Python
points_per_polygon = {}
for polygon_idx in range(n_polygons):
    current_polygon = polygons.iloc[polygon_idx,:]["geometry"]

    # manually loop over all points, check if polygon contains that point
    out_points = []
    for i in range(n_points):
        current_point = points.iloc[i, :]
        if current_polygon.contains(current_point["geometry"]):
            out_points.append(current_point.name)

    points_per_polygon[polygon_idx] = out_points
```

For about 500k points and 1000 polygons, the initial version of the code took about 20 hours to run.

Luckily, Shapely is built on top of NumPy, so she was able to apply functions to an array of points instead and wrote an improved version, which took just 20 minutes:

```Python
# 1) Extract points and corresponding names as two separate NumPy arrays from a larger data frame
# This will make it easier to apply vectorised functions below
points_array = np.array(points.loc[:,"geometry"])
point_names_array = np.array(points.loc[:,"name"])

points_per_polygon = {}
for polygon_idx in range(n_polygons):
    current_polygon = polygons.iloc[polygon_idx,:]["geometry"]

    # 2) apply `contains` to an array of points, rather than an individual point
    points_in_polygon_idx = current_polygon.contains(points_array)
    # 3) Filter `point_names_array` to get just the names of points contained in the polygon
    points_in_polygon = point_names_array[points_in_polygon_idx]
    # 4) Turn this array into a Python list and store it in output data
    points_per_polygon[polygon_idx] = points_in_polygon.tolist()
```

To vectorise this efficiently, the logic of the code had to be changed slightly:

1. The improved code starts by extracting the `shapely.Point`s and corresponding point names as two separate NumPy arrays from a larger data frame.
2. It then passes that array of points to `current_polygon.contains()`, which uses vectorisation to speed up the calculation. It returns a NumPy array of booleans (`True` or `False`), describing for each `Point` in the input array whether it is contained in `current_polygon`.
3. This boolean array is then [passed as an index](https://numpy.org/doc/stable/user/basics.indexing.html#boolean-array-indexing) to the `point_names_list` array. This returns a new array with the names of all points that are contained in the polygon (i.e. where the boolean array had the value `True`).
4. Finally, the contained points are stored as a Python list. (In this particular case, later parts of the data analysis code expected a list instead of a NumPy array. Since those parts of the code were "fast enough"—remember Donald Knuth’s quote in the earlier episode?—the researcher decided not to spend more time to rewrite them.)

::::::::::::::::::::::::::::::::::::: instructor

The following code snippet demonstrates how this works for a simplified example.

```Python
>>> from shapely import Point, Polygon
>>> import numpy as np
>>> polygon = Polygon([(0,0), (1,0), (1,1), (0,1), (0,0)])
>>> points_array = np.array((Point(0.1, 0.1), Point(0.5, 0.5), Point(2, 2)))
>>> point_names_array = np.array(("P1: Periphery", "P2: Centre", "P3: Outside"))
>>> points_in_polygon_idx = polygon.contains(points_array)
>>> points_in_polygon_idx
array([ True,  True, False])
>>> points_in_polygon = point_names_array[points_in_polygon_idx]
>>> points_in_polygon
array(['P1: Periphery', 'P2: Centre'], dtype='<U13')
>>> points_in_polygon.tolist()
['P1: Periphery', 'P2: Centre']
```

::::::::::::::::::::::::::::::::::::::::::::::::

<!--
TODO: The following example needs more work to be used by instructors other than me.
And since it’s not a very clean example (mixes np arrays and list comprehensions) and hard to extract a nice before/after snippet, maybe it’s better not to include this example in the general course materials? Or only in a callout or instructor note?
-->
<!--
### Example: Interpolating astrophysical spectra with AstroPy

This is from an open-source package I'm working on, so we can look at the actual pull request where I made this change: https://github.com/SNEWS2/snewpy/pull/310

&rightarrow; See the first table of benchmark results. Note that using a Python `for` loop to calculate the spectrum in 100 different time bins takes 100 times as long as for a single time bin. In the vectorized version, the computing time increases much more slowly.

(Note that energies were already vectorized—that's another factor of 100 we got "for free"!)

Code diff: https://github.com/SNEWS2/snewpy/pull/310/commits/0320b384ff22233818d07913c55c30f5968ae330
 -->

## Using Pandas (Effectively)

[Pandas](https://pandas.pydata.org/) is the most common Python package used for scientific computing when working with tabular data akin to spreadsheets (DataFrames).

Similar to NumPy, Pandas enables greater performance than pure Python implementations when used correctly, however incorrect usage can actively harm performance.

### Operating on Rows

Pandas' methods by default operate on columns. Each column or series can be thought of as a NumPy array, highly suitable for vectorisation.

Following the theme of this episode, iterating over the rows of a data frame using a `for` loop is not advised. The pythonic iteration will be slower than other approaches.

Pandas allows its own methods to be applied to rows in many cases by passing `axis=1`, where available these functions should be preferred over manual loops. Where you can't find a suitable method, `apply()` can be used, which is similar to `map()`, to apply your own function to rows.

```python
from timeit import timeit
import pandas
import numpy

N = 100000  # Number of rows in DataFrame

def genDataFrame():
    numpy.random.seed(12)  # Ensure each dataframe is identical
    return pandas.DataFrame(
    {
        "f_vertical": numpy.random.random(size=N),
        "f_horizontal": numpy.random.random(size=N),
        # todo some spurious columns
    })

def pythagoras(row):
    return (row["f_vertical"]**2 + row["f_horizontal"]**2)**0.5
    
def for_range():
    rtn = []
    df = genDataFrame()
    for row_idx in range(df.shape[0]):
        row = df.iloc[row_idx]
        rtn.append(pythagoras(row))
    return pandas.Series(rtn)

def for_iterrows():
    rtn = []
    df = genDataFrame()
    for row_idx, row in df.iterrows():
        rtn.append(pythagoras(row))
    return pandas.Series(rtn)
    
def pandas_apply():
    df = genDataFrame()
    return df.apply(pythagoras, axis=1)

repeats = 1000
gentime = timeit(genDataFrame, number=repeats)
print(f"for_range: {timeit(for_range, number=int(repeats/20))*20-gentime:.2f}ms")  # scale with factor 20, otherwise it takes too long
print(f"for_iterrows: {timeit(for_iterrows, number=int(repeats/20))*20-gentime:.2f}ms")
print(f"pandas_apply: {timeit(pandas_apply, number=int(repeats/20))*20-gentime:.2f}ms")
```

`apply()` is 4x faster than the two `for` approaches, as it avoids the Python `for` loop.


```output
for_range: 1582.47ms
for_iterrows: 1677.14ms
pandas_apply: 390.49ms
```

However, rows don't exist in memory as arrays (columns do!), so `apply()` does not take advantage of NumPy's vectorisation. You may be able to go a step further and avoid explicitly operating on rows entirely by passing only the required columns to NumPy.

::::::::::::::::::::::::::::::::::::: challenge

We can extract the individual columns of the data frame. These are of the type `pandas.Series`, which supports array broadcasting, just like a NumPy array.
Instead of using the `pythagoras(row)` function, can you write a vectorised version of this calculation?

```python
def vectorize():
    df = genDataFrame()
    vertical = df["f_vertical"]
    horizontal = df["f_horizontal"]

    # Your code goes here

    return pandas.Series(results)
```

Once you’ve done that, measure your performance by running
```python
repeats = 1000
gentime = timeit(genDataFrame, number=repeats)
print(f"vectorize: {timeit(vectorize, number=repeats)-gentime:.2f}ms")
```
What result do you find? Does this match your expectations?

:::::::::::::::::::::::: hint

Remember that most common mathematical operations work element-wise when applied to NumPy arrays.
For example:

```python
ar = np.array([1,2,3])

print(ar**2)  # array([1, 4, 9])
print(ar + ar)  # array([2, 4, 6])
```

:::::::::::::::::::::::::::::::::

:::::::::::::::::::::::: solution

```python
def vectorize():
    df = genDataFrame()
    vertical = df["f_vertical"]
    horizontal = df["f_horizontal"]

    result = numpy.sqrt(vertical**2 + horizontal**2)

    return pandas.Series(result)

print(f"vectorize: {timeit(vectorize, number=repeats)-gentime:.2f}ms")
```

264x faster than `apply()`, 1000x faster than the two `for` approaches!

```
vectorize: 1.48ms
```

:::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::::::::


It won't always be possible to take full advantage of vectorisation, for example you may have conditional logic.

An alternate approach is converting your DataFrame to a Python dictionary using `to_dict(orient='index')`. This creates a nested dictionary, where each row of the outer dictionary is an internal dictionary. This can then be processed via list-comprehension:

```python
def to_dict():
    df = genDataFrame()
    df_as_dict = df.to_dict(orient='index')
    return pandas.Series([(r['f_vertical']**2 + r['f_horizontal']**2)**0.5 for r in df_as_dict.values()])

print(f"to_dict: {timeit(to_dict, number=repeats)*10-gentime:.2f}ms")
```

Whilst still nearly 100x slower than pure vectorisation, it's twice as fast as `apply()`.

```sh
to_dict: 131.15ms
```

This is because indexing into Pandas' `Series` (rows) is significantly slower than a Python dictionary. There is a slight overhead to creating the dictionary (40ms in this example), however the stark difference in access speed is more than enough to overcome that cost for any large DataFrame.

```python
from timeit import timeit
import pandas as pandas

N = 100000  # Number of rows in DataFrame

def genInput():
    s = pandas.Series({'a' : 1, 'b' : 2})
    d = {'a' : 1, 'b' : 2}
    return s, d

def series():
    s, _ = genInput()
    for i in range(N):
        y = s['a'] * s['b']

def dictionary():
    _, d = genInput()
    for i in range(N):
        y = d['a'] * d['b']

repeats = 1000
print(f"series: {timeit(series, number=repeats):.2f}ms")
print(f"dictionary: {timeit(dictionary, number=repeats):.2f}ms")
```

65x slower!

```output
series: 237.25ms
dictionary: 3.63ms
```

### Filter Early

If you can filter your rows before processing, rather than after, you may significantly reduce the amount of processing and memory used.

::::::::::::::::::::::::::::::::::::: keypoints

- Python is an interpreted language, this adds an additional overhead at runtime to the execution of Python code. Many core Python and NumPy functions are implemented in faster C/C++, free from this overhead.
- NumPy can take advantage of vectorisation to process arrays, which can greatly improve performance.
- Many domain-specific packages are built on top of NumPy and can offer similar performance boosts.
- Pandas' data tables store columns as arrays, therefore operations applied to columns can take advantage of NumPy's vectorisation.

::::::::::::::::::::::::::::::::::::::::::::::::
