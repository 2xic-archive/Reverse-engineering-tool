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
	def __init__(self, unicorn, section_virtual_map, section_map, address_space):
		self.section_virtual_map = section_virtual_map
		self.section_map = section_map
		self.address_space = address_space
		self.unicorn = unicorn

		self.breakpoints = {

		}

		self.hook_points = {

		}

		self.memory_hooks = {
		
		}

		self.instruction_count = 0
		self.max_instructions = 4000

		self.address_hits = {

		}

		self.full_trace = False


		self.log_file = open("/root/test/test_binaries/unicorn.log", "w")

		self.registers_2_trace = {

		}

		self.values_2_look_for = set()

		self.next_break = False

	def add_breakpoint(self, address, identity="none"):
		self.breakpoints[address] = identity

	def add_hook(self, name, register_edits, spesification):
		self.hook_points[name] = [register_edits, spesification]

	def trace_registers(self, name, pause=False):
		self.registers_2_trace[name] = [eval("UC_X86_REG_{}".format(name.upper())), pause]

	def add_value_search(self, value):
		self.values_2_look_for.add(value)

	def add_hook_memory(self, address, write_only=False, read_only=False):
		assert type(address) == int, "input should be int"
		if not write_only and not read_only:
			self.memory_hooks[address] = 1
		elif(write_only):
			self.memory_hooks[address] = 0
		elif(read_only):
			self.memory_hooks[address] = -1

	def setup(self):
		self.register_state = {

		}
		for name, unicorn_refrence in self.registers_2_trace.items():
			self.register_state[name] = self.unicorn.reg_read(unicorn_refrence[0])

	def log_2_file(self):
		if(self.instruction_count > 0):
			self.log_file.write(hex(self.unicorn.reg_read(UC_X86_REG_RIP) - 0x400000) + "\n")
			self.log_file.write(hex(self.unicorn.reg_read(UC_X86_REG_ESI)) + "\n")


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

							if(self.check_memory_value(locations_number, check_only=True)):
								hook_mnemonic = "Memory value"

						locations = " ,".join(locations)
						string += "%s %s (%s);" % (dissably.mnemonic, dissably.op_str, locations)
					else:
						string += "%s %s;" % (dissably.mnemonic, dissably.op_str)
				else:
					string += "%s %s;" % (dissably.mnemonic, dissably.op_str)
				
				if(self.hook_points.get(str(dissably.mnemonic), None) != None):
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
		print("one step")
		self.next_break = True

	def memory_handle(self, tokens):

		for index, value in enumerate(tokens):
			if(value.startswith("0x")):
				tokens[index] = int(tokens[index], 16)
			elif not value.isdigit():
				tokens[index] = self.unicorn.reg_read(eval("UC_X86_REG_{}".format(value.upper())))

		if(len(tokens) == 2):
			print("Reading from 0x%x[%s] with size %i" % (tokens[0], self.determine_location(tokens[0]), tokens[1]))
			pretty_print_bytes(self.unicorn.mem_read(int(tokens[0]), int(tokens[1])))
		elif(len(tokens) == 1):
			print("Reading from 0x%x[%s] with size %i" % (tokens[0], self.determine_location(tokens[0]), 8))
			pretty_print_bytes(self.unicorn.mem_read(int(tokens[0]), 8))
		else:
			print("Add a address with size")

	def handle_commands(self, memory_access=False):
		if(memory_access):
			command = input("Memory access hit, write a command or press enter to continue\n")
		else:
			command = input("Breakpoint hit({}), write a command or press enter to continue\n".format(hex(self.current_address)))
		commands = {
			"view":self.get_register,
			"stepi":self.step,
			"memory":self.memory_handle
		}
		if(len(command) > 0):
			command_tokens = command.split(" ")
			if(commands.get(command_tokens[0], None) == None):
				print("command unknown...")
				return self.handle_commands()
			else:
				commands.get(command_tokens[0], None)(command_tokens[1:])
				if(command_tokens[0] != "stepi"):
					return self.handle_commands()
				return "stepi"



	def delta_registers(self):
		for name, unicorn_refrence in self.registers_2_trace.items():
			current_state =  self.unicorn.reg_read(unicorn_refrence[0])
			if(self.register_state[name] != current_state):
				if(name == "eflags".upper()):
					bold_print("\tlast instruction changed %s	[%s -> %s]" % (name, self.readable_eflags(self.register_state[name]), self.readable_eflags(current_state)))
				else:
					bold_print("\tlast instruction changed %s	[0x%x 0x%x]" % (name, self.register_state[name], current_state))

				if(unicorn_refrence[1] == True):
					input("Paused exec because of changed state\n")
				self.register_state[name] = current_state

	def resolve_hook_instruction(self):
		address, size = self.current_address, self.current_size
		instruction_name, hook_instruction, hook_name = self.get_instruction(address, size)
		print('\t\t%s' % instruction_name)

		if(hook_instruction or self.hook_points.get(hex(address), None) != None):
			if(hook_name == "Memory value"):
				self.handle_commands(memory_access=True)
				return False

			if(self.hook_points.get(hex(address), None) != None):
				hook_name = hex(address)

			spesification = self.hook_points[hook_name][1]
			max_hit_count = spesification.get("max_hit_count", None)


			hooked_IP = False # don't want to overwrite the hooked instruction pointer
			if(max_hit_count != None):
				current_count = spesification.get("count", 0)
				print("instruction got hooked (%i)" % (current_count))
				if(current_count <= max_hit_count):
					spesification["count"] = current_count + 1
				else:
					if(hook_instruction == False):
						raise Exception("hit max for %s" % (hex(address)))
					else:
						raise Exception("hit max for %s" % (hook_name))

				change_list = self.hook_points[hook_name][0].get(current_count, None)
				if(change_list == None):
					change_list = self.hook_points[hook_name][0].get(0, None)
					assert type(change_list) == dict, "need to provide default hook"

				for register, value in change_list.items():				
					if("RIP" in register.upper()):
						hooked_IP = True
					register = eval("UC_X86_REG_{}".format(register.upper()))
					self.unicorn.reg_write(register, value)
			else:
				print("instruction got hooked")
				for register, value in self.hook_points[hook_name][0].items():				
					if("RIP" in register.upper()):
						hooked_IP = True
					
					register = eval("UC_X86_REG_{}".format(register.upper()))
					self.unicorn.reg_write(register, value)

			if not hooked_IP:
				current_rip = self.unicorn.reg_read(UC_X86_REG_RIP)
				self.unicorn.reg_write(UC_X86_REG_RIP, current_rip + size)

			return True
		return False

	def memory_hook_check(self, address, write):
		assert type(address) == int, "input should be int"
		memory_hook_type = self.memory_hooks.get(address, None)
		if(memory_hook_type != None):
			if(write and memory_hook_type == 0 or memory_hook_type == 1):
				self.handle_commands(memory_access=True)
			elif(not write and memory_hook_type == -1):
				self.handle_commands(memory_access=True)

	def check_memory_value(self, value, check_only=False):
		if(value in self.values_2_look_for):
			if(check_only):
				return True
			self.handle_commands(memory_access=True)
		return False

	def resolve_break_point(self):
		self.current_breakpoint = self.breakpoints.get(self.unicorn.reg_read(UC_X86_REG_RIP), None)
		if(self.current_breakpoint != None or self.next_break):
			self.next_break = False
			if(type(self.current_breakpoint) == str):
				if(self.current_breakpoint == "check_mem"):
#					unicorn_debugger.add_breakpoint(0x400000 + 0x400dc5, "check_mem")
					pretty_print_bytes(self.unicorn.mem_read(0x400000 + 0x2b38b8 + 0x400dc5, 8))
					pretty_print_bytes(self.unicorn.mem_read(0x800dc5 + 0x2b38b8, 8))
					input("Breakpoint hit")
				elif(self.current_breakpoint == "exit"):
					print("will exit after commands")
					if not self.handle_commands() == "stepi":
						exit(0)
				else:
					self.handle_commands()
			else:
				self.handle_commands()


	def tick(self, address, size):
		try:
			if(self.address_hits.get(address) == None):
				self.address_hits[address] = 1
			else:
				self.address_hits[address] += 1

			self.log_2_file()
			self.delta_registers()

			self.current_address = address
			self.current_size = size
			
			if(self.resolve_hook_instruction()):
				#	the instruction did a patch ...
				return None

			self.resolve_break_point()
			
			self.instruction_count += 1

			if(self.max_instructions <= self.instruction_count):
				print("hit instruction_count limit. exited")
				exit(0)

		except Exception as e:
			print(e)
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			raise Exception("error in debugger")

	def print_registers(self):
		bold_print("\tRDI = 0x%x, RAX = 0x%x, RSP = 0x%x, RCX = 0x%x" % (self.unicorn.reg_read(UC_X86_REG_RDI),
													self.unicorn.reg_read(UC_X86_REG_RAX),
													self.unicorn.reg_read(UC_X86_REG_RSP),
													self.unicorn.reg_read(UC_X86_REG_RCX)
													)
		)

	def check_section_map(self, start, end, real_name):
		for name, value in self.section_virtual_map.items():
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

