import os
from numba import jit

@jit
def walk():
	for i in os.walk('.'):
		print(i)

walk()