import numpy as np
def find(x):
    a=[abs(y*x-round(y*x)) for y in range(1,50)]
    return a.index(np.min(a))+1
a=2.43
print a*find(a)
print round(a*find(a))
print find(a)