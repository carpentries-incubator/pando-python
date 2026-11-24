"""
Construct a graph demonstrating the difference in latencies relevant to code execution
Inspired by
https://gist.github.com/jboner/2841832
Using data from
https://www.intel.com/content/www/us/en/developer/articles/technical/memory-performance-in-a-nutshell.html
"""
import matplotlib.pyplot as plt
label = ["L1 cache", "L2 cache", "L3 cache", "RAM", "SSD", "HDD", "Atlantic round trip"]
latency_ns = [1, 4, 40, 80, 8000, 80000, 140000000]

plt.figure().set_figheight(2)
plt.barh(label, latency_ns)

plt.xlabel("Latency (nanoseconds)")
#plt.ylabel("")
plt.xscale('symlog')
plt.tight_layout()
plt.savefig('latency.png')
plt.show()
