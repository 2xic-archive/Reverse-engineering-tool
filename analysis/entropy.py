import sys
import numpy as np


def count(bins, start=0):
	table = {

	}
	for j in bins[start:]:
		if(table.get(j, None) == None):
			table[j] = 1
		else:
			table[j] += 1
	results = list(range(256))
	for j, k in sorted(table.items()):
		results[j] = k
	return np.array(results, dtype=np.uint8)

def entroyp(results):
	return (-np.sum(results * np.log(results), axis=0))

import matplotlib.pyplot as plt

file = open(sys.argv[1], "rb").read()

table = count(file)

print(entroyp(table))
