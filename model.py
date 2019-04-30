
from static.control_flow import *
from static.disassemble import *
import os
import pickle
import json


class model_configs():
	def __init__(self):
		self.load_code_only_sections = True


class model(model_configs):
	def __init__(self, static):
		super().__init__()


		self.static = static


		self.comments = {
			"0x400480":"hei"
		}

		self.decompile_binary()

		self.cfg = self.create_cfg()
		self.hex = self.parse_hex()

	def add_comment(self, address, content):
		self.comments[address] = content

	def resolve_comments(self, comments):
		for address, comment in comments.items():
			self.comments[address] = comment

	def get_working_dir(self):
		location = os.path.dirname(os.path.abspath(__file__)) 
		if not location.endswith("/"):
			location += "/"
		return location

	def get_text_location(self):
		location = os.path.dirname(os.path.abspath(__file__)) 
		if not location.endswith("/"):
			location += "/"
		return location + "text.pickle"

	def save_model(self, name):
		filehandler = open(self.get_working_dir() + name + ".pickle", "wb") 
		pickle.dump(self, filehandler)

	def load_comment(self):
		if(os.path.isfile(self.get_text_location())):
			pikcle_data = open(self.get_text_location(), "rb") 
			return json.loads(pickle.load(pikcle_data))
		return {}

	def save_comment(self):	
		filehandler = open(self.get_text_location(), "wb") 
		pickle.dump(json.dumps(self.custom_comments), filehandler)

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


	def decompile_binary(self):
		code_sections = self.static.get_sections_parsed()
		capstone_mode = get_capstone_mode(self.static.target_architecture, self.static.is_64_bit)

		self.decompiled_sections = {

		}
		for index, key in code_sections.items():
			text_content, virtual_address = self.static.read_section(key)
			decompiled, registered_touched, new_comments = decompile(text_content, virtual_address, capstone_mode, self.static.qword_helper)
			self.decompiled_sections[index] = [key, decompiled, registered_touched]

			self.resolve_comments(new_comments)

		if(self.load_code_only_sections):
			self.binary_sections = self.decompiled_sections
			return self.decompiled_sections

		self.binary_sections = {

		}

		for index, key in enumerate(self.static.sections_with_name.keys()):
			found = self.decompiled_sections.get(index, None)

			real_section = self.static.sections_with_name[key]

			if(real_section["size"] == 0):
				continue

			if(found == None):
				data = self.static.read_section_bytes(key)
				self.binary_sections[index] = [key,  data , []]
		
			else:
				self.binary_sections[index] = found

		return self.binary_sections
		
	def create_cfg(self):
		entrie_code_blocks = {

		}
		for index, key in self.static.code_sections.items():
			code = self.decompiled_sections[index][1]
			code_blocks = {

			}
			section_id = 0
			block = []

			found_control_flow = False
			for address, instruction in code.items():
				block.append({"address":address, "instruction":instruction[0], "argument":instruction[1]})

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
			entrie_code_blocks[key] = code_blocks
		

		return entrie_code_blocks

	def parse_hex(self):
		hex_file = self.static.file.hex()
		hex_parsed = []
		for i in range(0, len(hex_file), 2):
			hex_parsed.append(hex_file[i:i+2])
		return hex_parsed

	def get_cfg(self):
		return self.cfg
	
	def decompile_text(self):
		return self.binary_sections

