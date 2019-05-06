from capstone import *
from unicorn import *
import struct
import sys
import os
from unicorn.x86_const import *

def bold_print(text):
	print('\033[1m' + text + '\033[0m')

def bold_text(text):
	return '\033[1m' + text + '\033[0m'


def pretty_print_bytes(results):
	print(''.join('{:02x}'.format(x) for x in results ))
	return ''.join('{:02x}'.format(x) for x in results )



class unicorn_debug():
	def __init__(self, unicorn, section_viritual_map, section_map, address_space):
		self.section_viritual_map = section_viritual_map
		self.section_map = section_map
		self.address_space = address_space
		self.unicorn = unicorn

		self.breakpoints = {

		}

		self.hook_points = {

		}

		self.instruction_count = 0
		self.max_instructions = 100

		self.address_hits = {

		}

		self.full_trace = False


		self.log_file = open("/root/test/test_binaries/unicorn.txt", "w")


		self.instruction_hooks = {

		}

		self.registers_2_trace = {

		}

	def add_breakpoint(self, address, identity=""):
		self.breakpoints[address] = identity

	def add_hook_point(self, address, register=False, target_register=None, new_value=None, append=False):
		if(register):
			self.hook_points[address] = [int(register), target_register, new_value, append]
		else:
			self.hook_points[address] = [int(register), new_value, append]

	def log_2_file(self):
		if(self.instruction_count > 0):
			self.log_file.write(hex(self.unicorn.reg_read(UC_X86_REG_RIP) - 0x400000) + "\n")
			self.log_file.write(hex(self.unicorn.reg_read(UC_X86_REG_EFLAGS)) + "\n")


	def readable_eflags(self, current_state):
		flags =	[
				[2,	0x0004,	"PF"],	 
				[4,	0x0010,	"AF"],	
				[6,	0x0040,	"ZF"],	
				[7,	0x0080,	"SF"],	
				[8,	0x0100,	"TF"],	
				[9,	0x0200,	"IF"],	
				[10,	0x0400,	"DF"],	
				[11,	0x0800,	"OF"]
			]
		enabled_string = "0x%x	" % (current_state)

		for flag in flags:
			if( (current_state & flag[1]) >> flag[0]):
				enabled_string += flag[2] + " "
		return enabled_string

	def calculate_location(self, string="rdi, [rcx + rax*8 + 8]"):
		#rcx + rax*8 + 8
		strings = string.split(",")
		targets = []
		for string in strings:
			key_word = []
			current_word = ""

			block_words = ["[", "]", " ", ";"]
			math = ["*", "+", "-", "/"]
			for i in range(len(string)):
				if(string[i] in block_words):
					if(len(current_word) > 0):
						key_word.append(current_word)
						current_word = ""
					continue
				if(string[i] in math):
					if(len(current_word) > 0):
						key_word.append(current_word)
						current_word = ""
					key_word.append(string[i])
					continue
				current_word += string[i]

			if(len(current_word) > 0):
				key_word.append(current_word)

		#	print(key_word)
			results = ""
			register_hit = False
			for word in key_word:
				if(word in math):
					results += word
				else:
					if(word[0].isdigit()):
						results += str(word)
					else:
						try:
							register = eval("UC_X86_REG_{}".format(word.upper()))
							results += str(self.unicorn.reg_read(register))
							register_hit = True
						except Exception as e:
		#					print(e)
							pass
							# probably found qword

			if(len(results) > 0):
				targets.append(eval(results))

		if(len(targets) > 0):
			return targets
		return None

	def get_instruction(self, address, size):
		data = bytes(self.unicorn.mem_read(address, size))
		mode = Cs(CS_ARCH_X86, CS_MODE_64)
		string = ""
		hook_mnemonic = ""
		try:
			#print(data)
			for dissably in mode.disasm(data, 0x100):
				if(self.full_trace):
					location_argument = self.calculate_location(dissably.op_str + ";")
					if(location_argument != None):
						#print(location_argument)
						locations = []
						for locations_number in location_argument:
							locations.append(bold_text(self.determine_location(locations_number) + "[0x%x]" % (locations_number)))
						
						locations = " ,".join(locations)
						string += "%s %s (%s);" % (dissably.mnemonic, dissably.op_str, locations)
					else:
						string += "%s %s;" % (dissably.mnemonic, dissably.op_str)
				else:
					string += "%s %s;" % (dissably.mnemonic, dissably.op_str)
				
				if(self.instruction_hooks.get(str(dissably.mnemonic), None) != None):
					hook_mnemonic = dissably.mnemonic.strip()
					#hook_mnemonic = str(dissably.mnemonic)

		except Exception as e:
			print(e)
			print("get instruction bug")
		return string, len(hook_mnemonic) > 0, hook_mnemonic

	def get_register(self, name):
		if(name[0] == "eflags"):
			print(self.readable_eflags(self.unicorn.reg_read(UC_X86_REG_EFLAGS)))
		else:
			register = eval("UC_X86_REG_{}".format(name[0].upper()))
			print(hex(self.unicorn.reg_read(register)))

	def step(self, tokens):
		print("doing a step")
		self.breakpoints[self.current_address + self.current_size] = True

	def handle_commands(self):
		command = input("Breakpoint hit({}), write a command or press enter to continue\n".format(hex(self.current_address)))
		commands = {
			"view":self.get_register,
			"stepi":self.step
		}
		if(len(command) > 0):
			command_tokens = command.split(" ")
			if(commands.get(command_tokens[0], None) == None):
				print("command unkown...")
				return self.handle_commands()
			else:
				commands.get(command_tokens[0], None)(command_tokens[1:])
				if(command_tokens[0] != "stepi"):
					return self.handle_commands()

	def hook_instruction(self, name, register_edits):
		self.instruction_hooks[name] = register_edits


	def trace_registers(self, name):
		self.registers_2_trace[name] = eval("UC_X86_REG_{}".format(name.upper()))

	def setup(self):
		self.register_state = {

		}
		for name, unicorn_refrence in self.registers_2_trace.items():
			self.register_state[name] = self.unicorn.reg_read(unicorn_refrence)

	def delta_registers(self):
		for name, unicorn_refrence in self.registers_2_trace.items():
			current_state =  self.unicorn.reg_read(unicorn_refrence)
			if(self.register_state[name] != current_state):
				if(name == "eflags".upper()):
					bold_print("\tlast instruction changed %s	[%s -> %s]" % (name, self.readable_eflags(self.register_state[name]), self.readable_eflags(current_state)))
				else:
					bold_print("\tlast instruction changed %s	[0x%x 0x%x]" % (name, self.register_state[name], current_state))
				self.register_state[name] = current_state

	def tick(self, address, size):
		try:
			if(self.address_hits.get(address) == None):
				self.address_hits[address] = 1
			else:
				self.address_hits[address] += 1

		#	if(self.full_trace):
		#		self.print_registers()
			
			self.log_2_file()
			self.delta_registers()

			self.current_address = address
			self.current_size = size


			instruction_name, hook_instruction, hook_name = self.get_instruction(address, size)
			print('\t\t%s' % instruction_name)

			if(hook_instruction or self.instruction_hooks.get(hex(address), None) != None):
				print("instruction good hooked")
				if(self.instruction_hooks.get(hex(address), None) != None):
					hook_name = hex(address)

				for register, value in self.instruction_hooks[hook_name].items():				
					register = eval("UC_X86_REG_{}".format(register.upper()))
					self.unicorn.reg_write(register, value)
				
				current_rip = self.unicorn.reg_read(UC_X86_REG_RIP)
				self.unicorn.reg_write(UC_X86_REG_RIP, current_rip + size)
				return None

			hook = self.hook_points.get(self.unicorn.reg_read(UC_X86_REG_RIP), None)
			if(hook != None):
				# register, new value / target register, append/ new value, (append)
				if(hook[0] == 0):
					pass
				if(hook[0] == 1):
					if(hook[3] == True):
						value = self.unicorn.reg_read(hook[1])
						self.unicorn.reg_write(hook[1], hook[2] + value)
					else:
						self.unicorn.reg_write(hook[1], hook[2])
				self.unicorn.reg_write(UC_X86_REG_RIP, UC_X86_REG_RIP + size)
			

			custom_breakpoint = self.breakpoints.get(self.unicorn.reg_read(UC_X86_REG_RIP), None)
			if(custom_breakpoint != None):
				if(type(custom_breakpoint) == str):
					if(custom_breakpoint == "check_mem"):
#						unicorn_debugger.add_breakpoint(0x400000 + 0x400dc5, "check_mem")
						pretty_print_bytes(self.unicorn.mem_read(0x400000 + 0x2b38b8 + 0x400dc5, 8))
						pretty_print_bytes(self.unicorn.mem_read(0x800dc5 + 0x2b38b8, 8))
						input("Breakpoint hit")
				else:
					self.handle_commands()

			self.instruction_count += 1

			if(self.max_instructions <= self.instruction_count):
				print("hit instruction_count limit. exited")
				exit(0)
		except Exception as e:
			print(e)
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)

			raise Exception("bad")

	def print_registers(self):
		bold_print("\tRDI = 0x%x, RAX = 0x%x, RSP = 0x%x, RCX = 0x%x" % (self.unicorn.reg_read(UC_X86_REG_RDI),
													self.unicorn.reg_read(UC_X86_REG_RAX),
													self.unicorn.reg_read(UC_X86_REG_RSP),
													self.unicorn.reg_read(UC_X86_REG_RCX)
													)
		)

	def check_section_map(self, start, end, real_name):
		for name, value in self.section_viritual_map.items():
			if(value[0] < start and start < value[1]):
				print("overlap")
				print(name)
				print(real_name)
			if(value[0] < end and end < value[1]):
				print("overlap")
				print(name)
				print(real_name)

	def get_section(self, address):
		for name, item in self.section_map.items():
			if(item[0] < address and address < item[1]):
				return name
		return "unknown"

	def determine_location(self, address):
		section_check = self.get_section(address)
		if(section_check != "unknown"):
			return section_check

		for location_name, address_location in self.address_space.items():
			if(address_location[0] <= address and address <= address_location[1]):
				return location_name
		return "unknown"






