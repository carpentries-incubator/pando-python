---
title: "Understanding Latency"
teaching: 30
exercises: 0
---

:::::::::::::::::::::::::::::::::::::: questions

- Why is it faster to read/write a single 100 MB file, than 100 files of 1 MB each?
- How many orders of magnitude slower are disk accesses than RAM?
- What's the cost of creating a list?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

- Able to identify the relationship between different latencies relevant to software.
- Demonstrate how to implement parallel network requests.
- Justify the re-use of existing variables over creating new ones.

::::::::::::::::::::::::::::::::::::::::::::::::


## Accessing Disk

<!-- Read data from a file it goes disk->disk cache->ram->cpu cache/s->cpu -->
When reading data from a file, it is first transferred from the disk to the disk cache and then to the RAM (the computer's main memory, where variables are stored).
The latency to access files on disk is another order of magnitude higher than accessing normal variables.

As such, disk accesses benefit from sequential accesses and reading larger blocks together rather than single variables.
Python's `io` package is already buffered, so automatically handles this for you in the background.

However before a file can be read, the file system on the disk must be polled to transform the file path to its address on disk to initiate the transfer (or throw an exception).

Following the common theme of this episode, accessing randomly scattered files can be significantly slower than accessing a single larger file of the same size.
This is because for each file accessed, the file system must be polled to transform the file path to an address on disk. 
Traditional hard disk drives particularly suffer, as the read head must physically move to locate data.

Hence, it can be wise to avoid storing outputs in many individual files and to instead create a larger output file.

This is even visible outside of your own code. If you try to upload/download 1 GB to HPC.
The transfer will be significantly faster, assuming good internet bandwidth, if that's a single file rather than thousands.

The below example code runs a small benchmark, whereby 10MB is written to disk and read back whilst being timed. In one case this is as a single file, and in the other, 1000 file segments.

```python
import os, time

# Generate 10MB
data_len = 10000000
data = os.urandom(data_len)
file_ct = 1000
file_len = int(data_len/file_ct)
# Write one large file
start = time.perf_counter()
large_file = open("large.bin", "wb")
large_file.write(data)
large_file.close ()
large_write_s = time.perf_counter() - start
# Write multiple small files
start = time.perf_counter()
for i in range(file_ct):
    small_file = open(f"small_{i}.bin", "wb")
    small_file.write(data[file_len*i:file_len*(i+1)])
    small_file.close()
small_write_s = time.perf_counter() - start
# Read back the large file
start = time.perf_counter()
large_file = open("large.bin", "rb")
t = large_file.read(data_len)
large_file.close ()
large_read_s = time.perf_counter() - start
# Read back the small files
start = time.perf_counter()
for i in range(file_ct):
    small_file = open(f"small_{i}.bin", "rb")
    t = small_file.read(file_len)
    small_file.close()
small_read_s = time.perf_counter() - start
# Print Summary
print(f"{1:5d}x{data_len/1000000}MB Write: {large_write_s:.5f} seconds")
print(f"{file_ct:5d}x{file_len/1000}KB Write: {small_write_s:.5f} seconds")
print(f"{1:5d}x{data_len/1000000}MB Read: {large_read_s:.5f} seconds")
print(f"{file_ct:5d}x{file_len/1000}KB Read: {small_read_s:.5f} seconds")
print(f"{file_ct:5d}x{file_len/1000}KB Write was {small_write_s/large_write_s:.1f} slower than 1x{data_len/1000000}MB Write")
print(f"{file_ct:5d}x{file_len/1000}KB Read was {small_read_s/large_read_s:.1f} slower than 1x{data_len/1000000}MB Read")
# Cleanup
os.remove("large.bin")
for i in range(file_ct):
    os.remove(f"small_{i}.bin")
```

Running this locally, with an SSD I received the following timings.

```sh
    1x10.0MB Write: 0.00198 seconds
 1000x10.0KB Write: 0.14886 seconds
    1x10.0MB Read: 0.00478 seconds
 1000x10.0KB Read: 2.50339 seconds
 1000x10.0KB Write was 75.1 slower than 1x10.0MB Write
 1000x10.0KB Read was 523.9 slower than 1x10.0MB Read
```

Repeated runs show some noise to the timing, however the slowdown is consistently the same order of magnitude slower when split across multiple files.

You might not even be reading 1000 different files. You could be reading the same file multiple times, rather than reading it once and retaining it in memory during execution.
An even greater overhead would apply.

## Accessing the Network

When transferring files over a network, similar effects apply. There is a fixed overhead for every file transfer (no matter how big the file), so downloading many small files will be slower than downloading a single large file of the same total size.

Because of this overhead, downloading many small files often does not use all the available bandwidth. It may be possible to speed things up by parallelising downloads.

```Python
from concurrent.futures import ThreadPoolExecutor, as_completed
from timeit import timeit
import requests  # install with `pip install requests`


def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    return filename

downloaded_files = []

def sequentialDownload():
    for mass in range(10, 20):
        url = f"https://github.com/SNEWS2/snewpy-models-ccsn/raw/refs/heads/main/models/Warren_2020/stir_a1.23/stir_multimessenger_a1.23_m{mass}.0.h5"
        f = download_file(url, f"seq_{mass}.h5")
        downloaded_files.append(f)

def parallelDownload():
    # Initialise a pool of 6 threads to share the workload
    pool = ThreadPoolExecutor(max_workers=6)
    jobs = []
    # Submit each download to be executed by the thread pool
    for mass in range(10, 20):
        url = f"https://github.com/SNEWS2/snewpy-models-ccsn/raw/refs/heads/main/models/Warren_2020/stir_a1.23/stir_multimessenger_a1.23_m{mass}.0.h5"
        local_filename = f"par_{mass}.h5"
        jobs.append(pool.submit(download_file, url, local_filename))

    # Collect the results (and errors) as the jobs are completed
    for result in as_completed(jobs):        
        if result.exception() is None:
            # handle return values of the parallelised function
            f = result.result()
            downloaded_files.append(f)
        else:
            # handle errors
            print(result.exception())

    pool.shutdown(wait=False)


print(f"sequentialDownload: {timeit(sequentialDownload, globals=globals(), number=1):.3f} s")
print(downloaded_files)
downloaded_files = []
print(f"parallelDownload: {timeit(parallelDownload, globals=globals(), number=1):.3f} s")
print(downloaded_files)
```

Depending on your internet connection, results may vary significantly, but the parallel download will usually be quite a bit faster. Note also that the order in which the parallel downloads finish will vary.

```output
sequentialDownload: 3.225 s
['seq_10.h5', 'seq_11.h5', 'seq_12.h5', 'seq_13.h5', 'seq_14.h5', 'seq_15.h5', 'seq_16.h5', 'seq_17.h5', 'seq_18.h5', 'seq_19.h5']
parallelDownload: 0.285 s
['par_11.h5', 'par_12.h5', 'par_15.h5', 'par_13.h5', 'par_10.h5', 'par_14.h5', 'par_16.h5', 'par_19.h5', 'par_17.h5', 'par_18.h5']
```

## Latency Overview

Latency can have a big impact on the speed that a program executes, the below graph demonstrates this. Note the log scale!

![A graph demonstrating the wide variety of latencies a programmer may experience when accessing data.](episodes/fig/latency.png){alt="A horizontal bar chart displaying the relative latencies for L1/L2/L3 cache, RAM, SSD, HDD and a packet being sent from London to California and back. These latencies range from 1 nanosecond to 140 milliseconds and are displayed with a log scale."}

L1/L2/L3 caches are where your most recently accessed variables are stored inside the CPU, whereas RAM is where most of your variables will be found.

The lower the latency typically the higher the effective bandwidth (L1 and L2 cache have 1&nbsp;TB/s, RAM 100&nbsp;GB/s, SSDs up to 32 GB/s, HDDs up to 150&nbsp;MB/s), making large memory transactions even slower.

## Memory Allocation is not Free

<!-- Even "garbage collected" languages like Python have a cost. -->
When a variable is created, memory must be located for it, potentially requested from the operating system.
This gives it an overhead versus reusing existing allocations, or avoiding redundant temporary allocations entirely.

Within Python memory is not explicitly allocated and deallocated, instead it is automatically allocated and later "garbage collected". The costs are still there, this just means that Python programmers have less control over where they occur.

<!-- Based on the same premise as first example from Chapter 6 High Perf Python-->

The below implementation of the [heat-equation](https://en.wikipedia.org/wiki/Heat_equation), reallocates `out_grid`, a large 2 dimensional (500x500) list each time `update()` is called which progresses the model.

```python
grid_shape = (512, 512)

def update(grid, a_dt):
    x_max, y_max = grid_shape
    out_grid = [[0.0 for x in range(y_max)] * y_max for x in range(x_max)]
    for i in range(x_max):
        for j in range(y_max):
            out_xx = grid[(i-1)%x_max][j] - 2 * grid[i][j] + grid[(i+1)%x_max][j]
            out_yy = grid[i][(j-1)%y_max] - 2 * grid[i][j] + grid[i][(j+1)%y_max]
            out_grid[i][j] = grid[i][j] + (out_xx + out_yy) * a_dt 
    return out_grid
    
def heat_equation(steps):
    x_max, y_max = grid_shape
    grid = [[0.0] * y_max for x in range(x_max)]
    # Init central point to diffuse
    grid[int(x_max/2)][int(y_max/2)] = 1.0
    # Run steps
    for i in range(steps):
        grid = update(grid, 0.1)

heat_equation(100)
```

Line profiling demonstrates that function takes up over 55 seconds of the total runtime, with the cost of allocating the temporary `out_grid` list to be 39.3% of the total runtime of that function!

```output
Total time: 55.4675 s
File: heat_equation.py
Function: update at line 4

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
     3                                           @profile
     4                                           def update(grid, a_dt):
     5       100        127.7      1.3      0.0      x_max, y_max = grid_shape
     6       100   21822304.9 218223.0     39.3      out_grid = [[0.0 for x in range(y_max)] * y_max for x in range(x_m…
     7     51300       7741.9      0.2      0.0      for i in range(x_max):
     8  26265600    3632718.1      0.1      6.5          for j in range(y_max):
     9  26214400   11207717.9      0.4     20.2              out_xx = grid[(i-1)%x_max][j] - 2 * grid[i][j] + grid[(i+1…
    10  26214400   11163116.5      0.4     20.1              out_yy = grid[i][(j-1)%y_max] - 2 * grid[i][j] + grid[i][(…
    11  26214400    7633720.1      0.3     13.8              out_grid[i][j] = grid[i][j] + (out_xx + out_yy) * a_dt
    12       100         27.8      0.3      0.0      return out_grid
```

If instead `out_grid` is double buffered, such that two buffers are allocated outside the function, which are swapped after each call to update().

```python
grid_shape = (512, 512)

def update(grid, a_dt, out_grid):
    x_max, y_max = grid_shape
    for i in range(x_max):
        for j in range(y_max):
            out_xx = grid[(i-1)%x_max][j] - 2 * grid[i][j] + grid[(i+1)%x_max][j]
            out_yy = grid[i][(j-1)%y_max] - 2 * grid[i][j] + grid[i][(j+1)%y_max]
            out_grid[i][j] = grid[i][j] + (out_xx + out_yy) * a_dt 
    
def heat_equation(steps):
    x_max, y_max = grid_shape
    grid = [[0.0 for x in range(y_max)] for x in range(x_max)]
    out_grid = [[0.0 for x in range(y_max)] for x in range(x_max)]  # Allocate a second buffer once
    # Init central point to diffuse
    grid[int(x_max/2)][int(y_max/2)] = 1.0
    # Run steps
    for i in range(steps):
        update(grid, 0.1, out_grid)  # Pass the output buffer
        grid, out_grid = out_grid, grid  # Swap buffers

heat_equation(100)
```

The total time reduces to 34 seconds, reducing the runtime by 39% inline with the removed allocation.

```output
Total time: 34.0597 s
File: heat_equation.py
Function: update at line 3

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
     3                                           @profile
     4                                           def update(grid, a_dt, out_grid):
     5       100         43.5      0.4      0.0      x_max, y_max = grid_shape
     6     51300       7965.8      0.2      0.0      for i in range(x_max):
     7  26265600    3569519.4      0.1     10.5          for j in range(y_max):
     8  26214400   11291491.6      0.4     33.2              out_xx = grid[(i-1)%x_max][j] - 2 * grid[i][j] + grid[(i+1…
     9  26214400   11409533.7      0.4     33.5              out_yy = grid[i][(j-1)%y_max] - 2 * grid[i][j] + grid[i][(…
    10  26214400    7781156.4      0.3     22.8              out_grid[i][j] = grid[i][j] + (out_xx + out_yy) * a_dt
```

::::::::::::::::::::::::::::::::::::: keypoints

- One large file is preferable to many small files.
- Network requests can be parallelised to reduce the impact of fixed overheads.
- Memory allocation is not free, avoiding destroying and recreating objects can improve performance.

::::::::::::::::::::::::::::::::::::::::::::::::
