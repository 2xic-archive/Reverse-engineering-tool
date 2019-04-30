import sys
import numpy as np
import matplotlib.pyplot as plt


#	https://corte.si/posts/visualisation/binvis/index.html

#	this guy ^ has done a lot of cool stuff


file = open(sys.argv[1], "rb").read()

width = 1000
size = (len(file)//width) + 1
image = np.zeros((size, width, 3))

index_y = 0
index_x = 0

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

	if(file[index] == 0xFF):
		image[index_y, index_x, :] =  color_map["black"]
	elif(file[index] == 0x00):
		image[index_y, index_x, :] =  color_map["max"]
	elif(32 <= file[index] <= 127):
		image[index_y, index_x, :] =  color_map["print"]
	else:
		image[index_y, index_x, :] =  color_map["else"]


	index_x += 1

plt.imshow(image)
plt.show()


