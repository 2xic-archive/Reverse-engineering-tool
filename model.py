
from control_flow import *


class model:

	def __init__(self, static):
		self.static = static
		self.cfg = self.create_cfg()
		

	def create_cfg(self):
		ret_stop = []
		code = self.static.decompile_section(".text")
		for i in range(len(code)):
			ret_stop.append(code[i])
			if("ret" in code[i][1][0]):
				break
		return make_cfg(ret_stop)

	def get_cfg(self):
		return self.cfg
	
	def decompile_text(self):
		return self.static.decompile_text()

