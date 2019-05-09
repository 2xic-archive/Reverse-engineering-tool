def zigZag(arr):
	srt = sorted(arr)
	result = []

	left = 0
	right = len(srt)-1
	while left < right:
		result.append(srt[right])
		right -= 1
		if left < right:
			result.append(srt[left])
			left += 1
	return result

import matplotlib.pyplot as plt
import sys
import numpy as np

file = open(sys.argv[1], "rb").read()

width = 1000
size = (len(file)//width) + 1
image = np.zeros((size, width, 3))

index_y = 0
index_x = 0

file = zigZag(file)

for index in range(len(file)):
	if(index % (width) == 0 and index > 0):
		index_y += 1
		index_x = 0

	color_map = {
		"print":(255, 29, 0),
		"black":(0, 0, 0),
		"max":(255, 255,255),
		"else":(114, 113, 107)
	}
	val = file[index]
   # val = xy2d(val, index_x, index_y)
	#val = d2xy(25 )
	if(val == 0xFF):
		image[index_y, index_x, :] =  color_map["black"]
	elif(val == 0x00):
		image[index_y, index_x, :] =  color_map["max"]
	elif(32 <= val <= 127):
		image[index_y, index_x, :] =  color_map["print"]
	else:
		image[index_y, index_x, :] =  color_map["else"]


	index_x += 1

plt.imshow(image)
plt.show()
