import random
import sys
import time

# Argument parsing
if len(sys.argv) != 2:
    print("Script expects 1 positive integer argument, %u found."%(len(sys.argv) - 1))
    sys.exit()
n = int(sys.argv[1])

# Init
random.seed(12)
arr = [random.random() for i in range(n)]
print("Sorting %d elements"%(n))
start_time = time.monotonic()

# Sort
for i in range(n - 1):
    swapped = False
    for j in range(0, n - i - 1):
        if arr[j] > arr[j + 1]:
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
            swapped = True
    # If no two elements were swapped in the inner loop, the array is sorted
    if not swapped:
        break

end_time = time.monotonic()

# Validate
is_sorted = True
for i in range(n - 1):
    if arr[i] > arr[i+1]:
        is_sorted = False

print(f"Sorting: {'Passed' if is_sorted else 'Failed'} in {end_time - start_time:.3f} s")