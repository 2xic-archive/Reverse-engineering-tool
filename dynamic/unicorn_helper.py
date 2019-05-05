from capstone import *
from unicorn import *
import struct

from unicorn.x86_const import *

def bold_print(text):
	print('\033[1m' + text + '\033[0m')

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
		self.max_instructions = 10

		self.address_hits = {

		}

	def add_breakpoint(self, address):
		self.breakpoints[address] = True

	def add_hook_point(self, address, register=False, target_register=None, new_value=None, append=False):
		if(register):
			self.hook_points[address] = [int(register), target_register, new_value, append]
		else:
			self.hook_points[address] = [int(register), new_value, append]


	def calculate_location(self, string="rdi, [rcx + rax*8 + 8]"):
		#rcx + rax*8 + 8
		string = string.split(",")

		if(len(string) <= 1):
			return 0

		string = string[1]

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
		
		look_up_table = {
			"RDI":UC_X86_REG_RDI,
			"RAX":UC_X86_REG_RAX,
			"RSP":UC_X86_REG_RSP,
			"RCX":UC_X86_REG_RCX
		}

		results = ""
		for word in key_word:
			if(word in math):
				results += word
			else:
				if not word.isalpha():
					results += word
					continue
				data = look_up_table.get(word.upper(), None)
				if(data == None):
					results += "0"
			#		print("missing register name %s"  % ( word))
					continue
				results += str(self.unicorn.reg_read(data))
		return eval(results)

	def get_instruction(self, address, size):
		data = bytes(self.unicorn.mem_read(address, size))
		mode = Cs(CS_ARCH_X86, CS_MODE_64)
		string = ""
		for dissably in mode.disasm(data, 0x100):
			string += "%s %s; arg 2 = 0x%x  \n" % (dissably.mnemonic, dissably.op_str, self.calculate_location(dissably.op_str + ";"))
		return string

	def handle_commands(self):
		command = input("Breakpoint hit, write a command or press enter to continue")
		commands = {

		}
		
		if(len(command) > 0 and commands.get(command, None) == None):
			print("command unkown...")
			return self.handle_commands()

	def tick(self, address, size):
		if(self.address_hits.get(address) == None):
			self.address_hits[address] = 1
		else:
			self.address_hits[address] += 1

		print('\t\t%s' % (self.get_instruction(address, size)))

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
		
		if(self.breakpoints.get(self.unicorn.reg_read(UC_X86_REG_RIP), None) != None):
			self.handle_commands()

		self.instruction_count += 1

		if(self.max_instructions <= self.instruction_count):
			print("hit instruction_count limit. exited")
			exit(0)


	def print_registers(self):
		print("RDI = 0x%x, RAX = 0x%x, RSP = 0x%x" % (self.unicorn.reg_read(UC_X86_REG_RDI),
													self.unicorn.reg_read(UC_X86_REG_RAX),
													self.unicorn.reg_read(UC_X86_REG_RSP)))
	

	'''
		print("RDI = %s, RAX = %s, RSP = %s" % (
													determine_location(address_space, unicorn.reg_read(UC_X86_REG_RDI)),
													determine_location(address_space, unicorn.reg_read(UC_X86_REG_RAX)),
													determine_location(address_space, unicorn.reg_read(UC_X86_REG_RSP))))
	'''

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






