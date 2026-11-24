---
title: "Bonus Episode: Drop-in Replacements for Faster NumPy and Pandas"
teaching: 30
exercises: 20
---

:::::::::::::::::::::::::::::::::::::: questions

- What is a GPU?
- How can I run NumPy code on a GPU with almost no changes?
- How can I speed up Pandas, using either all my CPU cores or a GPU?
- Why do these tools make some code faster and not others?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

- Understand what a GPU is and when using one will (and won't) help with performance.
- Able to swap NumPy (and some SciPy) for DPNP or CuPy, and choose between them.
- Able to swap Pandas for Modin (CPU) or cuDF/hipDF (GPU), and explain how they differ.
- Able to time GPU and Modin code correctly, by waiting for the work to finish where needed.

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: instructor

- This episode introduces several "drop-in replacement" libraries, where changing an `import` line (or adding one or two) is enough to move work onto different hardware:

  - [DPNP](https://intelpython.github.io/dpnp/) runs NumPy code on Intel GPUs, including the integrated graphics found in most Intel laptops.
  - [CuPy](https://cupy.dev/) The same but for Nvidia and some AMD gpus.
  - [Modin](https://modin.readthedocs.io/) runs Pandas code across all CPU cores (it does **not** use the GPU).
  - [cuDF](https://docs.nvidia.com/cudf/latest/) runs Pandas code on NVIDIA GPUs, and [hipDF](https://rocm.docs.amd.com/projects/hipDF/en/latest/), AMD's port of cuDF, does the same on AMD Instinct GPUs.

- **The Numpy/Scipy examples are all "bi-lingual" between DPNP and CuPy.** This was a deliberate choice as provides the widest range of hardware support and allows most users to use there own laptops to run the examples. However, Unfortunately DPNP does not support apple silicon sorry MacOs people. with this in mind we have provided example outputs for each example so they can at least follow along. The examples and principles used in this material are near identical and fully transferable between CuPY and DPNP, you only need to change a few lines. So if you want to teach it with dedicated graphics hardware you can. Every GPU example is given in two tabs, "DPNP (Intel)" and "CuPy (NVIDIA or AMD)", each with its own measured output. The tabs are linked, so choosing CuPy once switches every example on the page.

- **The Pandas examples have three tabs: "Modin (any CPU)", "cuDF (NVIDIA)" and "hipDF (AMD)".** cuDF needs an NVIDIA GPU on Linux or WSL2, and hipDF currently only supports AMD Instinct datacenter GPUs, so many learners (Intel integrated graphics, Macs, Windows without WSL2) will not be able to run either. Modin is there to give them a non-GPU option that still fits the same workflow as the rest of the episode: change the import, warm up, wait for the work to finish when timing, and measure. **Stress that Modin is CPU only.** Its speed-ups come from using all the CPU cores, not from a GPU, which is why it helps with different operations to cuDF.

- cuDF and hipDF are used in "accelerator mode" (`import cudf.pandas; cudf.pandas.install()` before `import pandas`), which falls back to normal Pandas for anything that can't run on the GPU. hipDF is also imported as `cudf`, so the code in the two GPU tabs is identical.

- The plain Pandas baseline above the tabs was recorded with Pandas 3.0.6, the version cuDF installs. Modin installs an older Pandas, which is much slower (e.g. `apply()` 45.98 s vs 28.70 s), so the Modin tab compares against its own baseline. Pandas 3 alone beating Modin's `apply()` is a nice link back to the episode on keeping packages up to date.

- The challenge includes a `map()` that returns strings, which falls back to the CPU; `python -m cudf.pandas --profile` shows this, and it is a good discussion point.

- GPU programming is a massive topic in its own right and this episode only scratches the surface. Writing your own GPU kernels (e.g. with Numba or custom CuPy kernels) is possible but has been deliberately left out.

- **Performance results are very hardware dependent and can vary wildly.** The outputs shown were recorded on a single laptop (see the callout near the start of the episode). On that machine the integrated GPU gave a useful speed-up for heavier calculations (FFTs, linear algebra) but not for simple element-wise maths, while the dedicated NVIDIA GPU was dramatically faster at everything. Learners' results will differ, sometimes a lot; this is a teaching point, not a failure.

- **Displays can compete with integrated GPUs.** An integrated GPU also draws the desktop. While preparing this episode, using fractional display scaling on a high-resolution external monitor left the integrated GPU with under 10% of its normal compute speed, and slowed NumPy by around 3x as well. This was due to the memory bandwidth used to draw the screens. Turning scaling off restored full performance. If a learner's integrated GPU results look far worse than expected, you may wish to check whether they are using display scaling.

::::::::::::::::::::::::::::::::::::::::::::::::

## What is a GPU and why should I care?

Until now you have likely never had to give a second thought to what computer hardware is running your Python code. Most Python code runs on the computer's central processing unit (CPU). This can be thought of as the brain of your computer and is a computational "Swiss army knife".

CPUs are great for general purpose work, especially things that are sequential (one instruction followed by another), and they can even handle a modest amount of parallel work (running multiple instructions simultaneously). A typical laptop CPU has somewhere between 4 and 16 cores, so it can only work on that many things at the same time.

CPUs are also largely manufacturer agonistic, by which we mean 1 CPU will generally run the same software as another and perform roughly the same job, with only a slight difference in performance.

Graphics processing units (GPUs) by comparison are specialised processors designed for doing calculations in parallel. They were originally designed for graphics processing (hence the name) but these days have the ability to do more general calculations.

A GPU contains hundreds or thousands of small, simple cores that can all work on the same calculation at once in parallel. Thus If you have the same operation that needs to be done thousands (or even millions) of times, a GPU can be a huge help.

There are however, two things to keep in mind. Firstly the GPU usually has its own separate memory, so data must be copied to it before it can work, and copied back afterwards. Starting work on the GPU also has a small  fixed "startup" cost. Therefore a GPU only wins when there is lots of data with *a lot* of work to do on each piece.

![An animation of a CPU handing a large task to a GPU.](episodes/fig/what-a-gpu-does.gif){alt="An animation of a program that edits a photo in four steps: open the photo, resize it, brighten it and save it. The CPU, drawn as a chip with a few strong workers, does the first two steps itself. Step 3, brightening the photo, is a huge job, so the CPU sends it to the GPU, a chip with thousands of tiny workers. The photo slowly travels to the GPU one piece at a time, the GPU's workers all brighten it at the same moment, and the result travels slowly back to the CPU. During all of this the CPU sits idle, and a timeline bar along the bottom fills with 'Idle: waiting and doing nothing'. Once the result is back, the CPU wakes up and saves the photo. The final caption reads: GPUs are fast at big jobs, but the trips there and back are slow, and the CPU waits in between."}

The animation above shows this in action. The CPU works through the program, until it reaches a large task that the GPU is good at. The CPU then sends data over to the GPU for processing and waits for the result. Meanwhile, once the data arrives, the GPU does the work, then copies the result back to the CPU. The GPU itself is very fast, but if the trips there and back take too long, the CPU might have been better off doing the job itself.

Second, GPUs also vary between (and sometimes even within) manufactures as to what hardware and software they support. Whilst, we have tried our best to support the most common hardware setups, we cannot guarantee that every GPU will be able to work with all the examples in this episode. Therefore a good rule to follow is to always test and measure on *your* hardware before deciding if a change was worth it.

The example outputs shown were recorded on a laptop with:

- an Intel Core i7-12800H CPU (14 cores),
- Intel UHD integrated graphics,
- an NVIDIA T600 laptop GPU with 4 GB of memory,
- Linux using Python 3.12.

A more powerful integrated GPU, or a dedicated graphics card, may show very different results.

## Change one import: NumPy on the GPU (DPNP or CuPy)

There are two libraries which copy the NumPy interface, but run the work on a GPU:

- [DPNP](https://intelpython.github.io/dpnp/) (the Data Parallel Extension for NumPy) is from Intel and runs on Intel GPUs, including the integrated graphics in most Intel laptops.
- [CuPy](https://cupy.dev/) runs on NVIDIA graphics cards (and, on Linux, some AMD cards).

Because the functions have the same names as NumPy's, existing NumPy code can often be moved to the GPU by changing a single import.

Each GPU example in this episode has two tabs: one for DPNP and one for CuPy. Pick the one that matches your hardware; the tabs are linked, so your choice applies to every example on the page.

::::::::::::::::::::::::::::::::::::: callout

## Which should I use: DPNP or CuPy?

If your computer has a dedicated NVIDIA graphics card (or a supported AMD card on Linux), [CuPy](https://cupy.dev/) is the better option. It is more mature than DPNP, and it has much wider support for NumPy and SciPy functions.

DPNP's strength is that it runs on the integrated graphics found in most Intel laptops, so you can use it without a dedicated graphics card.

Instructions to install both can be found on the [setup page](../learners/setup.md).

:::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::: callout

## Will DPNP work on my laptop?

Note DPNP requires:

- Linux or Windows (unfortunately there is no macOS version),
- an Intel GPU (most Intel laptops from the last few years have integrated graphics that qualify),
- an up-to-date Intel graphics driver (see the [setup page](../learners/setup.md)).

You can check whether DPNP can see your GPU by running:

```sh
python -m dpctl --full-list
```

If a device is listed you are ready to go.

Note: If you have a Mac or otherwise dont have Intel graphics, we have provided sample outputs so you can follow along.
Also if you have an NVIDIA graphics card (or, on Linux, a supported AMD card), you can use CuPy instead: choose the "CuPy" tab in the examples below. Note: The Pandas section later in the episode includes a Modin option, which works on any laptop.

:::::::::::::::::::::::::::::::::::::::::::::

As an example, the following code smooths a large 4096×4096 greyscale "image" by converting it into frequencies with a Fast Fourier Transform (FFT), removing the high frequencies and converting it back.

```python
import numpy as np
from timeit import timeit

N = 4096
np.random.seed(42)
image = np.random.random((N, N)).astype(np.float32)

def smooth(image):
    freq = np.fft.fft2(image)               # convert to frequencies
    freq[N // 8 : -N // 8, :] = 0           # remove high frequencies
    freq[:, N // 8 : -N // 8] = 0
    return np.fft.ifft2(freq).real          # convert back to an image

repeats = 10
print(f"smooth: {timeit(lambda: smooth(image), number=repeats) / repeats:.3f} s")
```

```output
smooth: 0.855 s
```

To run this on the GPU, we change `import numpy as np` to `import dpnp as np` (or `import cupy as np`). Everything else stays the same, apart from one extra line which we will explain shortly.

::::::::::::::::::::::::::::::::::::: group-tab

### DPNP (Intel)

```python
import dpnp as np
from timeit import timeit

N = 4096
np.random.seed(42)
image = np.random.random((N, N)).astype(np.float32)

def smooth(image):
    freq = np.fft.fft2(image)               # convert to frequencies
    freq[N // 8 : -N // 8, :] = 0           # remove high frequencies
    freq[:, N // 8 : -N // 8] = 0
    result = np.fft.ifft2(freq).real        # convert back to an image
    result.sycl_queue.wait()                # wait for the GPU to finish
    return result

smooth(image)  # warm-up run
repeats = 10
print(f"smooth: {timeit(lambda: smooth(image), number=repeats) / repeats:.3f} s")
```

```output
smooth: 0.228 s
```

Almost 4x faster, from changing one line, on a modest integrated laptop GPU!

### CuPy (NVIDIA or AMD)

```python
import cupy as np
from timeit import timeit

N = 4096
np.random.seed(42)
image = np.random.random((N, N)).astype(np.float32)

def smooth(image):
    freq = np.fft.fft2(image)               # convert to frequencies
    freq[N // 8 : -N // 8, :] = 0           # remove high frequencies
    freq[:, N // 8 : -N // 8] = 0
    result = np.fft.ifft2(freq).real        # convert back to an image
    np.cuda.Device().synchronize()          # wait for the GPU to finish
    return result

smooth(image)  # warm-up run
repeats = 10
print(f"smooth: {timeit(lambda: smooth(image), number=repeats) / repeats:.3f} s")
```

```output
smooth: 0.013 s
```

Roughly 65x faster, from changing one line! Even an entry-level dedicated graphics card like this NVIDIA T600 has its own very fast memory and far more cores than integrated graphics, which share the computer's main memory with the CPU.

::::::::::::::::::::::::::::::::::::::::::::::::

Because `np.random.random()` is now the GPU library's version, `image` is created directly in the GPU's memory, and every operation on it runs on the GPU. The results of each operation also stay on the GPU, so no time is wasted copying data back and forth.

::::::::::::::::::::::::::::::::::::: callout

## Two important details

**The GPU works in the background.** When you call a DPNP or CuPy function, Python asks the GPU to start the work and then immediately carries on to the next line, without waiting for it to finish. This is great for performance, but it means a timer could stop before the GPU has actually done the work! To pause Python until the GPU has finished, use `result.sycl_queue.wait()` with DPNP, or `cupy.cuda.Device().synchronize()` with CuPy. You only need this when timing code. Anything that needs the actual values, such as `print(result)`, waits automatically.

**The first call is slow.** The first time a GPU function runs, the GPU code is prepared ("compiled") for your specific GPU. This is why the example calls `smooth()` once before timing it. In a real program this happens once, so it rarely matters.

:::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: caution

## GPUs and floating point accuracy

By default, numpy stores floating point numbers (decimals) with what is called 64-bit precision. Meanwhile Many GPUs, particularly Intel integrated graphics cannot work with 64-bit floating point numbers (`float64`, NumPy's default). On these devices DPNP will silently use 32-bit numbers (`float32`) instead.

**This sounds complicated**, fortunately, we don't need to go into technical details here. The plain English version is in numpy, calculations are by default accurate up 16 decimal places. However some GPUs are only accurate up to 7.

As such in these cases DPNP will silently continue and your calculations at a reduced accuracy. For many tasks this is fine, 7 decimal places is plenty accurate. However, if your results need high precision, you may wish to tread carefully. Fortunately, with DPNP you can check what the particular GPU you are using supports with:

```python
import dpctl
print(dpctl.select_default_device().has_aspect_fp64)
```

Thus, if this is a problem for your use case it may be worth putting in a check at the start to warn about any potential loss of accuracy.

Note: This mainly affects DPNP on Intel integrated graphics. NVIDIA and AMD graphics cards used with CuPy do support `float64` at full accuracy, although on most consumer cards it is many times slower than `float32`. Therefore you may wish to consider if you really need the accuracy or if you can accept the trade-off for more performance.

Note: In this episode we explicitly create data as `float32` everywhere using the `astype(np.float32)` method. This keeps everything comparable by forcing numpy to use 32-bit precision on CPU as well as GPU.

:::::::::::::::::::::::::::::::::::::::::::::

## When does the GPU *not* help?

A GPU is not magic, and on some hardware it can make code slower. The following example times the same calculation, `sqrt(x² + 1) × sin(x)`, done three ways: with a Python loop, with NumPy, and on the GPU, first for 1,000 numbers and then for 10 million.

::::::::::::::::::::::::::::::::::::: group-tab

### DPNP (Intel)

```python
import math
import numpy
import dpnp
from timeit import timeit

for N in (1_000, 10_000_000):
    numpy.random.seed(42)
    x_list = numpy.random.random(N).astype(numpy.float32).tolist()
    x_numpy = numpy.array(x_list, dtype=numpy.float32)
    x_gpu = dpnp.asarray(x_numpy)

    def python_loop():
        return [math.sqrt(v * v + 1) * math.sin(v) for v in x_list]

    def with_numpy():
        return numpy.sqrt(x_numpy * x_numpy + 1) * numpy.sin(x_numpy)

    def with_dpnp():
        result = dpnp.sqrt(x_gpu * x_gpu + 1) * dpnp.sin(x_gpu)
        result.sycl_queue.wait()
        return result

    with_dpnp()  # warm-up
    print(f"N = {N:,}")
    for f in (python_loop, with_numpy, with_dpnp):
        print(f"  {f.__name__}: {timeit(f, number=5) / 5:.5f} s")
```

```output
N = 1,000
  python_loop: 0.00011 s
  with_numpy: 0.00001 s
  with_dpnp: 0.00066 s
N = 10,000,000
  python_loop: 1.01007 s
  with_numpy: 0.03804 s
  with_dpnp: 0.04210 s
```

For 1,000 numbers, DPNP is approximately 66 times slower than NumPy, and even slower than the plain Python loop! For 10 million numbers, DPNP is no faster than NumPy on our example laptop.

### CuPy (NVIDIA or AMD)

```python
import math
import numpy
import cupy
from timeit import timeit

for N in (1_000, 10_000_000):
    numpy.random.seed(42)
    x_list = numpy.random.random(N).astype(numpy.float32).tolist()
    x_numpy = numpy.array(x_list, dtype=numpy.float32)
    x_gpu = cupy.asarray(x_numpy)

    def python_loop():
        return [math.sqrt(v * v + 1) * math.sin(v) for v in x_list]

    def with_numpy():
        return numpy.sqrt(x_numpy * x_numpy + 1) * numpy.sin(x_numpy)

    def with_cupy():
        result = cupy.sqrt(x_gpu * x_gpu + 1) * cupy.sin(x_gpu)
        cupy.cuda.Device().synchronize()
        return result

    with_cupy()  # warm-up
    print(f"N = {N:,}")
    for f in (python_loop, with_numpy, with_cupy):
        print(f"  {f.__name__}: {timeit(f, number=5) / 5:.5f} s")
```

```output
N = 1,000
  python_loop: 0.00009 s
  with_numpy: 0.00001 s
  with_cupy: 0.00005 s
N = 10,000,000
  python_loop: 1.06577 s
  with_numpy: 0.04910 s
  with_cupy: 0.00329 s
```

For 1,000 numbers, CuPy is several times slower than NumPy. For 10 million numbers, it is about 15x faster than NumPy, because a dedicated graphics card has its own, much faster, memory.

::::::::::::::::::::::::::::::::::::::::::::::::

Two things stand out:

- **Small amounts of data are slower on the GPU.** Each operation has a fixed cost for starting work on the GPU, which for small amounts of data can easily take longer than the work itself.
- **Simple calculations may not benefit on integrated graphics.** Each operation here does very little maths per number, so the time is mostly spent reading and writing memory. An integrated GPU shares the same memory as the CPU, so it has little or no advantage. A dedicated graphics card, with its own fast memory, still does well.

Notice that switching from a Python loop to NumPy was a *20x* or more speed-up, which is a reminder that vectorising your code with NumPy is the first, and often the biggest, step.

### Copying data to and from the GPU

Data must be copied between normal (CPU) memory and the GPU. This is generally handled automatically when you use a DPNP or CuPy function. However, these copies take time, so if you are doing multiple operations on GPU. Or doing some work on GPU and some more on CPU. It is generally best to move your data to the GPU once, do as much work there as possible, then copy the results back.

The `asarray()` function (`dpnp.asarray()` or `cupy.asarray()`) copies a NumPy array to the GPU and `asnumpy()` (`dpnp.asnumpy()` or `cupy.asnumpy()`) copies a GPU array back to NumPy.

::::::::::::::::::::::::::::::::::::: group-tab

### DPNP (Intel)

```python
import numpy
import dpnp
from timeit import timeit

N = 4096
numpy.random.seed(42)
image = numpy.random.random((N, N)).astype(numpy.float32)   # lives in CPU memory
image_gpu = dpnp.asarray(image)                             # copied to the GPU once

def fft_numpy():
    return numpy.fft.fft2(image)

def fft_gpu_data_already_there():
    result = dpnp.fft.fft2(image_gpu)
    result.sycl_queue.wait()
    return result

def fft_gpu_copy_every_time():
    result = dpnp.fft.fft2(dpnp.asarray(image))   # copy to GPU
    return dpnp.asnumpy(result)                    # copy back to CPU

fft_gpu_data_already_there(); fft_gpu_copy_every_time()  # warm-up
repeats = 10
for f in (fft_numpy, fft_gpu_data_already_there, fft_gpu_copy_every_time):
    print(f"{f.__name__}: {timeit(f, number=repeats) / repeats:.3f} s")
```

```output
fft_numpy: 0.646 s
fft_gpu_data_already_there: 0.111 s
fft_gpu_copy_every_time: 0.152 s
```

In this case copying to and from the GPU every time adds over a third to the runtime, but it is still much faster than NumPy because an FFT does a lot of work per number.

### CuPy (NVIDIA or AMD)

```python
import numpy
import cupy
from timeit import timeit

N = 4096
numpy.random.seed(42)
image = numpy.random.random((N, N)).astype(numpy.float32)   # lives in CPU memory
image_gpu = cupy.asarray(image)                             # copied to the GPU once

def fft_numpy():
    return numpy.fft.fft2(image)

def fft_gpu_data_already_there():
    result = cupy.fft.fft2(image_gpu)
    cupy.cuda.Device().synchronize()
    return result

def fft_gpu_copy_every_time():
    result = cupy.fft.fft2(cupy.asarray(image))   # copy to GPU
    return cupy.asnumpy(result)                    # copy back to CPU

fft_gpu_data_already_there(); fft_gpu_copy_every_time()  # warm-up
repeats = 10
for f in (fft_numpy, fft_gpu_data_already_there, fft_gpu_copy_every_time):
    print(f"{f.__name__}: {timeit(f, number=repeats) / repeats:.3f} s")
```

```output
fft_numpy: 0.738 s
fft_gpu_data_already_there: 0.006 s
fft_gpu_copy_every_time: 0.057 s
```

Copying to and from the graphics card every time makes this almost 10x slower! The FFT itself is so fast that the copying, which has to travel over the connection between the CPU and the graphics card, now takes most of the time. It is still much faster than NumPy, but the data should be kept on the GPU wherever possible.

::::::::::::::::::::::::::::::::::::::::::::::::

For simpler calculations, the copying alone can take longer than doing the whole job on the CPU.

::::::::::::::::::::::::::::::::::::: callout

## Rules of thumb

A GPU is most likely to help when:

- there is a lot of data (millions of numbers, not thousands),
- each number needs a lot of maths (e.g. FFTs, large matrix operations, image processing),
- the data can stay on the GPU between steps.

And whatever you change, always time it on your own hardware!

:::::::::::::::::::::::::::::::::::::::::::::

## What about SciPy?

DPNP's main focus is NumPy. Its support for SciPy is limited to a handful of functions inside `dpnp.scipy`, such as `dpnp.scipy.linalg.lu_factor()` and `lu_solve()` for solving systems of linear equations. CuPy has much wider SciPy support, inside `cupyx.scipy`. Where a function exists, the pattern is the same: swap the import.

::::::::::::::::::::::::::::::::::::: group-tab

### DPNP (Intel)

```python
import numpy
import scipy.linalg
import dpnp
import dpnp.scipy.linalg

N = 4096
numpy.random.seed(0)
A = numpy.random.random((N, N)).astype(numpy.float32) + N * numpy.eye(N, dtype=numpy.float32)
b = numpy.random.random(N).astype(numpy.float32)

# SciPy, on the CPU
x = scipy.linalg.lu_solve(scipy.linalg.lu_factor(A), b)

# DPNP, on the GPU
A_gpu, b_gpu = dpnp.asarray(A), dpnp.asarray(b)
x_gpu = dpnp.scipy.linalg.lu_solve(dpnp.scipy.linalg.lu_factor(A_gpu), b_gpu)
```

On our example laptop the DPNP version took 0.14 s, compared to 0.32 s for SciPy: a little over twice as fast, even though SciPy's linear algebra already uses every CPU core.

### CuPy (NVIDIA or AMD)

```python
import numpy
import scipy.linalg
import cupy
import cupyx.scipy.linalg

N = 4096
numpy.random.seed(0)
A = numpy.random.random((N, N)).astype(numpy.float32) + N * numpy.eye(N, dtype=numpy.float32)
b = numpy.random.random(N).astype(numpy.float32)

# SciPy, on the CPU
x = scipy.linalg.lu_solve(scipy.linalg.lu_factor(A), b)

# CuPy, on the GPU
A_gpu, b_gpu = cupy.asarray(A), cupy.asarray(b)
x_gpu = cupyx.scipy.linalg.lu_solve(cupyx.scipy.linalg.lu_factor(A_gpu), b_gpu)
```

On our example laptop the CuPy version took 0.07 s, compared to 0.37 s for SciPy: about 5x faster, even though SciPy's linear algebra already uses every CPU core.

::::::::::::::::::::::::::::::::::::::::::::::::

If you rely heavily on SciPy and have a dedicated graphics card, CuPy is a much better route. Its [`cupyx.scipy`](https://docs.cupy.dev/en/stable/reference/scipy.html) module covers large parts of SciPy, including `fft`, `signal`, `ndimage`, `sparse`, `linalg`, `special`, `stats` and `interpolate`, again with the same function names.

::::::::::::::::::::::::::::::::::::: challenge

## Is it worth it?

The function below calculates the average power spectrum of 2,000 recorded signals.

```python
import numpy as np
from timeit import timeit

np.random.seed(1)
signals = np.random.random((2_000, 16_384)).astype(np.float32)  # 2000 recordings

def average_spectrum(signals):
    spectra = np.abs(np.fft.rfft(signals, axis=1)) ** 2
    result = spectra.mean(axis=0)
    return result

print(f"average_spectrum: {timeit(lambda: average_spectrum(signals), number=10) / 10:.3f} s")
```

Convert it to use DPNP (or CuPy) and time both versions. Is the GPU version faster on your computer?

:::::::::::::::::::::::: hint

Remember the two details: wait for the GPU to finish before the timer stops, and do a "warm-up" run before timing.

:::::::::::::::::::::::::::::::::

:::::::::::::::::::::::: solution

::::::::::::::: group-tab

### DPNP (Intel)

```python
import dpnp as np
from timeit import timeit

np.random.seed(1)
signals = np.random.random((2_000, 16_384)).astype(np.float32)  # 2000 recordings

def average_spectrum(signals):
    spectra = np.abs(np.fft.rfft(signals, axis=1)) ** 2
    result = spectra.mean(axis=0)
    result.sycl_queue.wait()
    return result

average_spectrum(signals)
print(f"average_spectrum: {timeit(lambda: average_spectrum(signals), number=10) / 10:.3f} s")
```

On the laptop used for this episode:

```output
NumPy: average_spectrum: 0.456 s
DPNP:  average_spectrum: 0.312 s
```

The integrated GPU was about 1.5x faster than NumPy here. Your results may be completely different, and the integrated GPU may even be slower!

### CuPy (NVIDIA or AMD)

```python
import cupy as np
from timeit import timeit

np.random.seed(1)
signals = np.random.random((2_000, 16_384)).astype(np.float32)  # 2000 recordings

def average_spectrum(signals):
    spectra = np.abs(np.fft.rfft(signals, axis=1)) ** 2
    result = spectra.mean(axis=0)
    np.cuda.Device().synchronize()
    return result

average_spectrum(signals)
print(f"average_spectrum: {timeit(lambda: average_spectrum(signals), number=10) / 10:.3f} s")
```

On the laptop used for this episode:

```output
NumPy: average_spectrum: 0.249 s
CuPy:  average_spectrum: 0.006 s
```

In This case the NVIDIA card was around 40x faster than NumPy here. Your results may be completely different!

:::::::::::::::::::::::::::::::::

The key take away here is that changing the import is easy, but you should always measure before and after to check it actually helped.

:::::::::::::::::::::::::::::::::
:::::::::::::::::::::::::::::::::::::::::::::::

## Faster Pandas: Modin (CPU) or cuDF/hipDF (GPU)

There are also drop-in replacements for Pandas. Just like DPNP and CuPy, you switch them on with a line or two at the top of your script, and the rest of your code stays the same. We will look at three:

- [Modin](https://modin.readthedocs.io/) does **not** use the GPU. Pandas normally does all its work on a single CPU core. Modin splits your DataFrame into pieces and works on them using *all* of your CPU cores at the same time. Most laptops have 4-16 cores, so for the right kind of work this can give a good speed-up, and it works on any laptop.
- [cuDF](https://docs.nvidia.com/cudf/latest/) is from NVIDIA and runs Pandas code on NVIDIA graphics cards (Linux or WSL2 only).
- [hipDF](https://rocm.docs.amd.com/projects/hipDF/en/latest/) is AMD's version of cuDF, for AMD Instinct GPUs.

Each Pandas example has three tabs, one for each library. If you don't have a suitable GPU, choose the Modin tab.

### Modin

To use Modin, change the import:

```python
import modin.pandas as pd
```

Behind the scenes, Modin hands the work to an "engine" which manages the CPU cores. We will use [Ray](https://www.ray.io/), which is the default and usually the fastest.

::::::::::::::::::::::::::::::::::::: callout

If you are using an Intel Mac or WSL on Windows, Ray may not work. Use the Dask engine instead: install `modin[dask]`, and use `modin.config.Engine.put("dask")` in the examples below.

:::::::::::::::::::::::::::::::::::::::::::::

### cuDF and hipDF

cuDF and hipDF are both used through their *Pandas accelerator mode*. Rather than changing the import, you add two lines **before** `import pandas`:

```python
import cudf.pandas
cudf.pandas.install()
import pandas as pd
```

From then on, any Pandas operation that cuDF supports runs on the GPU. Anything it doesn't support quietly falls back to normal Pandas on the CPU, so your code still works, it just won't be any faster for that step.

You can also turn on accelerator mode without changing your script at all, by running it with:

```sh
python -m cudf.pandas my_script.py
```

hipDF is imported with the same name, `cudf`, so the code is identical on NVIDIA and AMD; only the installation is different.

::::::::::::::::::::::::::::::::::::: callout

## Will hipDF work on my computer?

Probably not, unless you are using an HPC system. hipDF currently only supports AMD **Instinct** datacenter GPUs (such as the MI210, MI250 and MI300X) on Linux. Consumer Radeon graphics cards are not supported. To use accelerator mode, hipDF also needs you to run `export HSA_XNACK=1` before starting Python. See the [setup page](../learners/setup.md) for details.

:::::::::::::::::::::::::::::::::::::::::::::

### Trying them out

First, we'll create a large CSV file of (made up) weather readings from 1,000 stations, with 10 million rows (about 140 MB):

```python
import numpy as np
import pandas as pd

N = 10_000_000
rng = np.random.default_rng(1)
pd.DataFrame({
    "station": rng.integers(0, 1000, N),
    "temperature": rng.normal(10, 5, N).round(2),
    "rainfall": rng.exponential(2, N).round(2),
}).to_csv("weather.csv", index=False)
```

The following Pandas code reads the file, then performs a row-by-row `apply()`, a `map()` and a `groupby()`.

```python
import time
import pandas as pd

def timed(label, func):
    start = time.perf_counter()
    result = func()
    print(f"{label}: {time.perf_counter() - start:.2f} s")
    return result

def feels_like(row):
    if row["rainfall"] > 5:
        return row["temperature"] - 3
    return row["temperature"]

df = timed("read_csv", lambda: pd.read_csv("weather.csv"))
timed("apply", lambda: df.apply(feels_like, axis=1))
timed("map", lambda: df["temperature"].map(lambda t: t * 9 / 5 + 32))
timed("groupby", lambda: df.groupby("station").mean())
```

```output
read_csv: 1.60 s
apply: 28.70 s
map: 1.78 s
groupby: 0.17 s
```

These timings use Pandas 3.0.6, the version installed alongside cuDF.

Now the same code with each replacement. In each case a few lines at the top change, plus a "warm-up" so that the timings are fair.

::::::::::::::::::::::::::::::::::::: group-tab

### Modin (any CPU)

```python
import time
import modin.pandas as pd
import modin.config
from modin.utils import execute

modin.config.Engine.put("ray")
pd.DataFrame({"warm_up": [1]}).sum()   # start Ray before we time anything

def timed(label, func):
    start = time.perf_counter()
    result = func()
    execute(result)                    # wait for Modin to finish
    print(f"{label}: {time.perf_counter() - start:.2f} s")
    return result

def feels_like(row):
    if row["rainfall"] > 5:
        return row["temperature"] - 3
    return row["temperature"]

df = timed("read_csv", lambda: pd.read_csv("weather.csv"))
timed("apply", lambda: df.apply(feels_like, axis=1))
timed("map", lambda: df["temperature"].map(lambda t: t * 9 / 5 + 32))
timed("groupby", lambda: df.groupby("station").mean())
```

```output
read_csv: 1.26 s
apply: 19.19 s
map: 0.70 s
groupby: 0.24 s
```

Modin installs an older version of Pandas, so to keep the comparison fair we timed plain Pandas in the same environment as Modin. There, `read_csv()` took 1.44 s, `apply()` 45.98 s, `map()` 2.75 s and `groupby()` 0.19 s.

Compared with that, `apply()` is now 2.4x faster and `map()` almost 4x faster. These run a Python function once for every row, which is exactly the kind of slow work that benefits from being split across many cores. `read_csv()` is a little faster, and `groupby()` is actually slightly slower, because Pandas already does this efficiently and Modin adds the cost of splitting the work up.

Notice that just using Pandas 3 (28.70 s, above) runs `apply()` faster than Modin does with the older Pandas. As the episode on [keeping packages up to date](optimisation-use-latest.md) explains, upgrading can give a free speed-up, so check that first.

### cuDF (NVIDIA)

```python
import time
import cudf.pandas
cudf.pandas.install()
import pandas as pd

pd.DataFrame({"warm_up": [1]}).sum()   # start the GPU before we time anything

def timed(label, func):
    start = time.perf_counter()
    result = func()
    print(f"{label}: {time.perf_counter() - start:.2f} s")
    return result

def feels_like(row):
    if row["rainfall"] > 5:
        return row["temperature"] - 3
    return row["temperature"]

df = timed("read_csv", lambda: pd.read_csv("weather.csv"))
timed("apply", lambda: df.apply(feels_like, axis=1))
timed("map", lambda: df["temperature"].map(lambda t: t * 9 / 5 + 32))
timed("groupby", lambda: df.groupby("station").mean())
```

```output
read_csv: 0.60 s
apply: 0.49 s
map: 0.14 s
groupby: 0.12 s
```

Everything is faster, but by very different amounts. `apply()` went from almost 29 seconds to under half a second, about 60x faster, and `map()` is about 13x faster. This may be surprising, since a Python function is normally run one row at a time. However, cuDF can translate ("compile") simple numerical Python functions, like `feels_like()`, into GPU code, which then runs on many rows at once. Most of the 0.49 s is this compiling, which happens the first time a function is used: running the same `apply()` a second time took just 0.01 s.

`read_csv()` is about 2.7x faster, but `groupby()` only gained a little, because Pandas already does it efficiently and 10 million rows is not much work for a GPU.

### hipDF (AMD)

```python
import time
import cudf.pandas
cudf.pandas.install()
import pandas as pd

pd.DataFrame({"warm_up": [1]}).sum()   # start the GPU before we time anything

def timed(label, func):
    start = time.perf_counter()
    result = func()
    print(f"{label}: {time.perf_counter() - start:.2f} s")
    return result

def feels_like(row):
    if row["rainfall"] > 5:
        return row["temperature"] - 3
    return row["temperature"]

df = timed("read_csv", lambda: pd.read_csv("weather.csv"))
timed("apply", lambda: df.apply(feels_like, axis=1))
timed("map", lambda: df["temperature"].map(lambda t: t * 9 / 5 + 32))
timed("groupby", lambda: df.groupby("station").mean())
```

The code is identical to the cuDF version. Remember to run `export HSA_XNACK=1` before starting Python.

```output
TODO(AMD): replace with measured output
```

TODO(AMD): describe the hipDF results, and how they compare with cuDF.

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: callout

## Waiting for the work to finish

Just like DPNP and CuPy, Modin starts work and then lets Python carry on before it has finished. When *timing* Modin code, use `modin.utils.execute()` to wait for the work to complete, otherwise operations can appear to take almost no time at all. Starting Ray also takes a few seconds the first time Modin is used, which is why the example runs a small "warm-up" calculation first.

cuDF and hipDF are different. Even though the work happens on the GPU, in practice cuDF waits for the GPU to finish each Pandas operation before Python carries on. So, unlike CuPy's `synchronize()` or Modin's `execute()`, **no extra line is needed when timing cuDF or hipDF**. We checked this: adding `cupy.cuda.Device().synchronize()` to the cuDF example made no difference to the timings. Starting the GPU does take a moment the first time, so the cuDF and hipDF examples still have a warm-up.

<!-- TODO(AMD): confirm that adding a synchronise call also makes no difference to the hipDF timings. -->

You don't need any of these in normal code; Modin waits automatically whenever you look at the results.

:::::::::::::::::::::::::::::::::::::::::::::

### When it doesn't help

Splitting work between CPU cores, or starting work on a GPU, has a cost. For small DataFrames that cost is far larger than the work itself:

::::::::::::::::::::::::::::::::::::: group-tab

### Modin (any CPU)

```python
from timeit import timeit
import pandas
import modin.pandas as mpd
import modin.config
from modin.utils import execute

modin.config.Engine.put("ray")
small_pandas = pandas.DataFrame({"a": range(1000), "b": range(1000)})
small_modin = mpd.DataFrame({"a": range(1000), "b": range(1000)})
execute(small_modin.sum())  # warm-up

print(f"pandas: {timeit(lambda: small_pandas.sum(), number=100) / 100:.5f} s")
print(f"modin:  {timeit(lambda: execute(small_modin.sum()), number=100) / 100:.5f} s")
```

```output
pandas: 0.00005 s
modin:  0.04548 s
```

Almost 1000x slower!

### cuDF (NVIDIA)

```python
from timeit import timeit
import cudf.pandas
cudf.pandas.install()
import pandas as pd

small = pd.DataFrame({"a": range(1000), "b": range(1000)})
small.sum()  # warm-up

print(f"cudf.pandas: {timeit(lambda: small.sum(), number=100) / 100:.5f} s")
```

```output
cudf.pandas: 0.00205 s
```

About 50x slower than plain Pandas, which took 0.00004 s in the same environment, because every operation has the fixed cost of starting work on the GPU.

### hipDF (AMD)

```python
from timeit import timeit
import cudf.pandas
cudf.pandas.install()
import pandas as pd

small = pd.DataFrame({"a": range(1000), "b": range(1000)})
small.sum()  # warm-up

print(f"cudf.pandas: {timeit(lambda: small.sum(), number=100) / 100:.5f} s")
```

```output
TODO(AMD): replace with measured output
```

TODO(AMD): compare with plain Pandas (0.00004 s).

::::::::::::::::::::::::::::::::::::::::::::::::

Modin, cuDF and hipDF are all designed for DataFrames with millions of rows. For small data, plain Pandas is best.

Also remember the advice from the earlier episode on [scientific Python packages](optimisation-numpy.md): replacing `apply()` with vectorised column operations, e.g. `df["temperature"] * 9 / 5 + 32`, is often far faster than running a Python function for every row, and works without any extra libraries.

::::::::::::::::::::::::::::::::::::: callout

## What ran on the GPU?

When cuDF can't run an operation on the GPU, it falls back to normal Pandas on the CPU without telling you. To see what ran where, run your script with the `--profile` option:

```sh
python -m cudf.pandas --profile my_script.py
```

When the script finishes, this prints a table of the Pandas functions that were called, showing how many ran on the GPU and how many on the CPU, and lists any that needed to fall back. In Jupyter, put `%%cudf.pandas.profile` at the top of a cell instead.

:::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: challenge

## Speed up a Pandas script

The following script labels each reading by temperature, marks "wet and cold" readings, then counts them. It uses the `weather.csv` file we created earlier.

```python
import time
import pandas as pd

start = time.perf_counter()
df = pd.read_csv("weather.csv")
df["season_label"] = df["temperature"].map(lambda t: "cold" if t < 5 else "mild" if t < 15 else "warm")
df["wet"] = df.apply(lambda row: row["rainfall"] > 2 and row["temperature"] < 10, axis=1)
counts = df.groupby("season_label")["wet"].sum()
print(counts)
print(f"total: {time.perf_counter() - start:.2f} s")
```

Convert it to use Modin, or cuDF/hipDF if you have a suitable GPU, and compare the total runtime. Which lines do you expect to benefit the most?

:::::::::::::::::::::::: hint

For Modin, only the import needs to change. For cuDF or hipDF, add `import cudf.pandas` and `cudf.pandas.install()` before `import pandas`. Because the script prints `counts` at the end, Modin has to finish all its work before the timer stops, so `execute()` isn't needed here.

:::::::::::::::::::::::::::::::::

:::::::::::::::::::::::: solution

::::::::::::::: group-tab

### Modin (any CPU)

```python
import time
import modin.pandas as pd
import modin.config

modin.config.Engine.put("ray")

start = time.perf_counter()
df = pd.read_csv("weather.csv")
df["season_label"] = df["temperature"].map(lambda t: "cold" if t < 5 else "mild" if t < 15 else "warm")
df["wet"] = df.apply(lambda row: row["rainfall"] > 2 and row["temperature"] < 10, axis=1)
counts = df.groupby("season_label")["wet"].sum()
print(counts)
print(f"total: {time.perf_counter() - start:.2f} s")
```

```output
pandas total: 41.71 s
modin total: 22.29 s
```

For our machine this was almost twice as fast. Which is not bad for changing one line (Note: this time includes Ray starting up, and the Pandas time is for the older Pandas that Modin installs). The `map()` and `apply()` lines, which run a Python function for every row, benefit the most.

### cuDF (NVIDIA)

```python
import time
import cudf.pandas
cudf.pandas.install()
import pandas as pd

start = time.perf_counter()
df = pd.read_csv("weather.csv")
df["season_label"] = df["temperature"].map(lambda t: "cold" if t < 5 else "mild" if t < 15 else "warm")
df["wet"] = df.apply(lambda row: row["rainfall"] > 2 and row["temperature"] < 10, axis=1)
counts = df.groupby("season_label")["wet"].sum()
print(counts)
print(f"total: {time.perf_counter() - start:.2f} s")
```

```output
pandas total: 29.95 s
cudf total: 3.37 s
```

About 9x faster, which includes starting the GPU. However, not every line ran on the GPU. Running the script with `python -m cudf.pandas --profile` shows:

```output
Not all pandas operations ran on the GPU. The following functions required CPU
fallback:
- Series.map
```

The `map()` function returns text ("cold", "mild" or "warm"), which cuDF can't compile into GPU code, so that line ran in normal Pandas on the CPU. At about 2.6 s it was most of the total. The `apply()`, which only uses numbers, did run on the GPU and benefits the most.

### hipDF (AMD)

```python
import time
import cudf.pandas
cudf.pandas.install()
import pandas as pd

start = time.perf_counter()
df = pd.read_csv("weather.csv")
df["season_label"] = df["temperature"].map(lambda t: "cold" if t < 5 else "mild" if t < 15 else "warm")
df["wet"] = df.apply(lambda row: row["rainfall"] > 2 and row["temperature"] < 10, axis=1)
counts = df.groupby("season_label")["wet"].sum()
print(counts)
print(f"total: {time.perf_counter() - start:.2f} s")
```

```output
TODO(AMD): replace with measured output
```

TODO(AMD): describe the hipDF result, including which lines fell back to the CPU (check with `python -m cudf.pandas --profile`).

:::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::
:::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: keypoints

- GPUs have thousands of simple cores and are good at doing the same calculation on large amounts of data, but copying data to the GPU and starting work there both have a cost.
- DPNP can run NumPy code on Intel GPUs (including laptop integrated graphics) by changing `import numpy as np` to `import dpnp as np`. However, Its SciPy support is limited to a few functions.
- CuPy does the same for NVIDIA (and, on Linux, some AMD) graphics cards with `import cupy as np`. If you have one, it is the better choice: it is more mature and covers much more of NumPy and SciPy (via `cupyx.scipy`).
- Modin runs Pandas code across all CPU cores (not the GPU) by changing `import pandas as pd` to `import modin.pandas as pd`. It works on any computer, and helps most with row-by-row operations on large DataFrames.
- cuDF (NVIDIA) and hipDF (AMD Instinct) run Pandas code on the GPU by adding `import cudf.pandas` and `cudf.pandas.install()` before `import pandas`. Anything they can't run on the GPU falls back to normal Pandas on the CPU, which `python -m cudf.pandas --profile` will show.
- DPNP, CuPy and Modin work in the background, so wait for them to finish when timing code. cuDF and hipDF wait automatically.
- None of them help with small data, and results are very hardware dependent: always measure on your own computer.

::::::::::::::::::::::::::::::::::::::::::::::::
