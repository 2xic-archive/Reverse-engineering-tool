
from static.control_flow import *
from static.disassemble import *
import os
import pickle
import json
from dynamic.emulator import *
from .grapth import *


class model_configs():
	def __init__(self):
		self.load_code_only_sections = True


import threading
def threaded(function):
	def wrapper(*args, **kwargs):
		thread = threading.Thread(target=function, args=args, kwargs=kwargs)
		thread.start()
		return thread
	return wrapper


class model(model_configs):
	def __init__(self, static, socket_io, auto_boot=True, disable_args=False):
		super().__init__()
		self.static = static

		self.comments = {
	
		}

		self.binary_sections = {

		}

		self.socket_io = socket_io
		
		self.cfg = OrderedDict()

		self.hex = None

		self.done_decompile = False
		self.decompile_binary()

		self.dynamic = emulator(self.static, disable_args=disable_args)
		if auto_boot:
			self.run_emulator()
		self.ran_emulator = False

	#	self.cfg = self.create_CFG()
		self.hex = self.parse_hex()

	def run_emulator(self, force=False, non_stop=False, thread=True):
		if not self.socket_io == None or force:
			if(thread):
				self.dynamic.run_thread(non_stop)
			else:
				self.dynamic.run(non_stop)
			self.ran_emulator = True

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

	def save_model(self, name):
		filehandler = open(self.get_working_dir() + name + ".pickle", "wb") 
		pickle.dump(self, filehandler)

	@threaded
	def decompile_binary(self):
		import time
		code_sections = self.static.get_sections_parsed()
		capstone_mode = get_capstone_mode(self.static.target_architecture, self.static.is_64_bit)

		self.decompiled_sections = OrderedDict()
		for index, key in code_sections.items():
#			print("Targett == {}".format(key))
			text_content, virtual_address = self.static.read_section(key)
			decompiled, registered_touched, new_comments = decompile(text_content, virtual_address, capstone_mode, self.static.qword_helper)
			self.decompiled_sections[key] = {"section_name":key, 
												"code":decompiled, 
												"registers":registered_touched
											}

			grapth = self.create_CFG_partial(self.decompiled_sections[key]["code"], key)
			self.resolve_comments(new_comments)

			if(self.socket_io != None):
				self.socket_io.emit("block", {"code":self.decompiled_sections,
						 "sections":self.static.section_sizes,
						 "grapth":self.cfg
					})

		self.done_decompile = True

#			print("parsed another section")
#			time.sleep(10) # (used to debug)
#		print("done loading....")
		if(self.load_code_only_sections):
			self.binary_sections = self.decompiled_sections
			return self.decompiled_sections

		self.binary_sections = {

		}

		for index, key in enumerate(self.static.sections_with_name.keys()):
			found = self.decompiled_sections.get(index, None)

			section = self.static.sections_with_name[key]

			if(section["size"] == 0):
				continue

			if(found == None):
				data = self.static.read_section_bytes(key)
				self.binary_sections[index] = [key,  data , []]
		
			else:
				self.binary_sections[index] = found
		return self.binary_sections

	def create_CFG_partial(self, code, key):
		code_blocks = OrderedDict()

		section_id = 0
		block = []

		found_control_flow = False
			
		for address, instruction in code.items():
			block.append({"address":int(address, 16), "instruction":instruction["instruction"], "argument":instruction["argument"]})

			if("jne" in instruction["instruction"] or "je" in instruction["instruction"]):
				found_control_flow = True
				pass

			if("ret" in instruction["instruction"] or "hlt" in instruction["instruction"] or ("jmp" in instruction["instruction"]  and not found_control_flow)):
				code_blocks[section_id] = make_cfg(block)
				section_id += 1
				block = []
				found_control_flow = False
				
		self.cfg[key] = code_blocks
		return code_blocks

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

