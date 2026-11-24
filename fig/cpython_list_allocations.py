"""
Construct a graph demonstrating the number of re-allocations
if growing a CPython List with append()
"""
t = 0
a = 0
x = range(1000000)

allocs = [0 for x in range(1000000)]
while t < 1000000:
    t += 1
    t_old = t
    # https://github.com/python/cpython/blob/a571a2fd3fdaeafdfd71f3d80ed5a3b22b63d0f7/Objects/listobject.c#L74
    t = t + (t >> 3) + 6
    a+=1
    for k in range(t_old, t+1):
        if k < len(allocs):
            allocs[k] = a
    
import matplotlib.pyplot as plt

plt.plot(x, allocs)

plt.xlabel("Appends")
plt.ylabel("Resizes")
#plt.ticklabel_format(style='plain')
#plt.xscale('symlog')
plt.savefig('cpython_list_allocations.png')
plt.show()