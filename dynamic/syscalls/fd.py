'''
	
	file descriptor format

'''

class file_descriptor:
	def __init__(self, fd_count, file):
		# the first two fd's are pre-defined
		self.fd_number = 2 + (fd_count + 1) 
		self.file_name = file[:-1]
#		self.file = open(file[:-1], "r")

	def __eq__(self, other):
		if(other == self.fd_number):
			return True
		return False