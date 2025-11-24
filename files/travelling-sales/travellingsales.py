"""
Naive brute force travelling salesperson
python travellingsales.py <cities>
"""

import itertools
import math
import random
import sys
import time

def distance(point1, point2):
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

def total_distance(points, order):
    total = 0
    for i in range(len(order) - 1):
        total += distance(points[order[i]], points[order[i + 1]])
    return total + distance(points[order[-1]], points[order[0]])

def traveling_salesman_brute_force(points):
    min_distance = float('inf')
    min_path = None
    for order in itertools.permutations(range(len(points))):
        d = total_distance(points, order)
        if d < min_distance:
            min_distance = d
            min_path = order
    return min_path, min_distance

# Argument parsing
if len(sys.argv) != 2:
    print("Script expects 1 positive integer argument, %u found."%(len(sys.argv) - 1))
    sys.exit()
cities_len = int(sys.argv[1])
if cities_len < 1:
    print("Script expects 1 positive integer argument, %s converts < 1."%(sys.argv[1]))
    sys.exit()
# Define the cities as (x, y) coordinates
random.seed(12) # Fixed random for consistency
cities = [(0,0)]
for i in range(cities_len):
    cities.append((random.uniform(-1, 1), random.uniform(-1, 1)))

# Find the shortest path
start_time = time.monotonic()
shortest_path, min_distance = traveling_salesman_brute_force(cities)
end_time = time.monotonic()

print("Cities:", cities_len)
print("Shortest Path:", shortest_path)
print("Shortest Distance:", min_distance)
print(f"Execution time: {end_time - start_time:.3f} s")
