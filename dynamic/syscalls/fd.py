'''
	
	file descriptor format

'''
import os
class file_descriptor:
	def __init__(self, fd_count, file):
		# the first two fd's are pre-defined
		self.fd_number = 2 + (fd_count + 1) 
		self.file_name = file[:-1]

		#	/lib/x86_64-linux-gnu/libc.so.6
	#	if(self.file_name == "/lib/x86_64-linux-gnu/tls/x86_64/libc.so.6"):
	#		self.file_name = "/lib/x86_64-linux-gnu/libc.so.6"

		self.file_position = 0
#		self.file = open(file[:-1], "r")

	def __eq__(self, other):
		if(other == self.fd_number):
			return True
		return False

	def does_file_exist(self):
		return os.path.isfile(self.file_name)

	def return_fd(self, mode="r"):
		if not self.does_file_exist():
			return None
		return open(self.file_name, mode)