
from static.control_flow import *


class model:

	def __init__(self, static):
		self.static = static
		self.cfg = self.create_cfg()
		self.hex = self.parse_hex()
	#	self.hex_print()
	#	print(self.cfg)

	def hex_print(self):
		for j in range(0, len(self.hex), 12):
			content = ""
			string = ""
			for q in range(12):
				content += self.hex[j + q] + " "
				if(int(self.hex[j + q], 16) == 0):
					string += "."
				else:
					string += chr(int(self.hex[j + q], 16))
			print("%s 	|%s" % (content, string))

	def create_cfg(self):
		entrie_code_blocks = {

		}
		for j in self.static.code_sections:		
			code = self.static.decompile_section(j)
			code_blocks = {

			}
			section_id = 0
			block = []

			found_control_flow = False
			for address, instruction in code.items():
				block.append({"address":address, "instruction":instruction[0], "argument":instruction[1]})
#				if("jmp" in instruction[0]  and not found_control_flow):
				if("jne" in instruction[0] or "je" in instruction[0]):
					found_control_flow = True
					pass

				if("ret" in instruction[0] or "hlt" in instruction[0] or "jmp" in instruction[0]  and not found_control_flow):
					code_blocks[section_id] = make_cfg(block)
					section_id += 1
					block = []
					found_control_flow = False

			if(0 < len(block)):
				code_blocks[section_id] = make_cfg(block)
			entrie_code_blocks[j] = code_blocks
		
			#if(j == ".text"):
			#	print(code_blocks[1])
			#	test_graphviz(code_blocks[1])
		
		#if(j == ".plt"):
		#	print(entrie_code_blocks[])
	#	print(entrie_code_blocks[".init"])
	#	print(test_hirachy(entrie_code_blocks[".init"][0]))
	#	exit(0)

		#		exit(0)
		return entrie_code_blocks
#		exit(0)
#		return 

	def parse_hex(self):
		hex_file = self.static.file.hex()
		hex_parsed = []
		for i in range(0, len(hex_file), 2):
			hex_parsed.append(hex_file[i:i+2])
		return hex_parsed

	def get_cfg(self):
		return self.cfg
	
	def decompile_text(self):
		return self.static.decompile_text()




