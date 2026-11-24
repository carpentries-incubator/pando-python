import time

"""
This is a synthetic program intended to produce a clear profile with cProfile/snakeviz
Function names, constructed from a hex digit and a number clearly denote their position in the hierarchy.
"""
def a_1():
    for i in range(3):
        b_1()
    time.sleep(1)
    b_2()

    
def b_1():
    c_1()
    c_2()

def b_2():
    time.sleep(1)
    
def c_1():
    time.sleep(0.5)


def c_2():
    time.sleep(0.3)
    d_1()

def d_1():
    time.sleep(0.1)




# Entry Point
a_1()