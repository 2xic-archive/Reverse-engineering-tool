from capstone import *
from unicorn import *
import struct
import sys
import os
from unicorn.x86_const import *
from common.interface import *
from keystone import *
from common.printer import *
from inspect import isfunction
from .helper_scripts.stack_string import hex_2_string
import hashlib

def pretty_print_bytes(results, aschii=True, logging=True):
	if(logging):
		print("")
		print(''.join('0x{:02x} '.format(x) for x in results ))
	if(aschii and logging):
		print(''.join((chr(x) if( 0 < x < 128) else " ") for x in results ))
	if(logging):
		print("")
	return ''.join('{:02x}'.format(x) for x in results )




class unicorn_debug():
	def __init__(self, emulator_class, section_virtual_map, section_map, address_space, logging, non_stop=False):
		self.section_virtual_map = section_virtual_map
		self.section_map = section_map
		self.address_space = address_space
		self.parrent = emulator_class
		self.unicorn = emulator_class.emulator
		self.logging = logging

		self.non_stop = non_stop


		self.branch_logs = [

		]

		self.breakpoints = {

		}

		self.breakpoints_hits = {

		}

		self.hook_points = {

		}

		self.memory_hooks = {
		
		}

		self.address_hits = {

		}

		self.registers_2_trace = {

		}

		self.jump_op_list = {

		}

		self.values_2_look_for = set()
		self.patch_values = {

		}
		self.print_at_address = {

		}

		self.instruction_count = 0
		self.max_instructions = 0x3710 #0xdeafbeef #100

		self.full_trace = False

		self.logging_enabled = os.path.isfile('/root/test/test_binaries/unicorn.log')

		if(self.logging_enabled):
			self.log_file = open("/root/test/test_binaries/unicorn.log", "w")


		self.next_break = False
		self.next_jump = False
		self.next_size = 0
		self.test = False

		self.current_address = 0x41414141

	def view_stack(self, end, string, length=8, count=4):
		print("stack layout")
		current_string = ""
		jump_count = 0
		for index, char in enumerate(string):
			current_string += char
			if(len(current_string) == length):
				if(jump_count == 0):
					print("{}".format(hex(end)), end="	")

				print(current_string, end=" ")
				current_string = ""
				jump_count += 1
						
				if(jump_count % count == 0 and jump_count > 0):
					end += 16
					print("\n{}".format(hex(end)), end="	")
		print(current_string)


	def add_breakpoint(self, address, identity="none"):
		assert(type(address) == int)
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

	def pop_branch(self):
		'''
			need to check that branch is a function first.
		'''
		pass
	#	self.branch_logs.pop()

	def get_branches(self, tokens):
		print(self.branch_logs)

	def log_2_file(self, address=None):
		if(not self.log_file.closed and 0 < self.instruction_count and self.logging_enabled):
			if(address == None):
				self.log_file.write(hex(self.unicorn.reg_read(UC_X86_REG_RIP)) + "\n")
			else:
				self.log_file.write(hex(address) + "\n")	
			self.log_file.write(hex(self.unicorn.reg_read(UC_X86_REG_EFLAGS)) + "\n")

			#self.log_file.write(self.readable_eflags(self.unicorn.reg_read(UC_X86_REG_EFLAGS)) + "\n")
			#self.log_file.write(hex(self.unicorn.reg_read(UC_X86_REG_RAX)) + "\n")

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
			if((current_state & flag[1]) >> flag[0]):
				enabled_string += flag[2] + " "
		return enabled_string

	#	basic parser, nothing fancy
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
			for dissably in mode.disasm(data, 0x100):
				if(self.full_trace):
					location_argument = self.calculate_location(dissably.op_str + ";")
					if(location_argument != None):
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
			print(self.determine_location(self.unicorn.reg_read(register)))

	def step(self, tokens):
		print("one instruction step")
		self.print_instruction([])
		self.next_break = True

	def parse_math(self, stream):
		look_a_side_buffer = ""
		results = 0

		sign = 1 
		for i in stream:
			if(i == "+" or i == "-"):
				if(look_a_side_buffer.startswith("0x")):
					results += (sign * int(look_a_side_buffer, 16))
				elif(look_a_side_buffer.isdigit()):
					results += (sign * int(look_a_side_buffer))
				elif(look_a_side_buffer.lower() == "ld"):
					results += (sign * self.parrent.look_up_library["ld-linux-x86-64.so.2"][0])
				elif(look_a_side_buffer.lower() == "libc"):
					results += (sign * self.parrent.look_up_library["libc.so.6"][0])
				else:
					results += (sign * self.unicorn.reg_read(eval("UC_X86_REG_{}".format(look_a_side_buffer.upper()))))
				
				if(i == "+"):
					sign = 1
				elif(i == "-"):
					sign = -1
				else:
					raise Exception("non supported arithmetic")
				look_a_side_buffer = ""
			else:
				look_a_side_buffer += i

		if(look_a_side_buffer.startswith("0x")):
			results += (sign * int(look_a_side_buffer, 16))
		elif(look_a_side_buffer.isdigit()):
			results += (sign * int(look_a_side_buffer))
		elif(look_a_side_buffer.lower() == "ld"):
			results += (sign * self.parrent.look_up_library["ld-linux-x86-64.so.2"][0])
		elif(look_a_side_buffer.lower() == "libc"):
			results += (sign * self.parrent.look_up_library["libc.so.6"][0])		
		else:
			results += (sign * self.unicorn.reg_read(eval("UC_X86_REG_{}".format(look_a_side_buffer.upper()))))
				
		return results

	def memory_handle(self, tokens):
		for index, value in enumerate(tokens):
			tokens[index] = self.parse_math(tokens[index])
#			if(value.startswith("0x")):
#				tokens[index] = int(tokens[index], 16)
#			elif not value.isdigit():
#				tokens[index] = self.unicorn.reg_read(eval("UC_X86_REG_{}".format(value.upper())))

		if(len(tokens) == 2):
			print("Reading from 0x%x[%s] with size %i" % (tokens[0], self.determine_location(tokens[0]), tokens[1]))
			pretty_print_bytes(self.unicorn.mem_read(int(tokens[0]), int(tokens[1])))
		elif(len(tokens) == 1):
			print("Reading from 0x%x[%s] with size %i" % (tokens[0], self.determine_location(tokens[0]), 8))
			pretty_print_bytes(self.unicorn.mem_read(int(tokens[0]), 8))
		else:
			print("Add a address with size")

	def peek_stack(self, tokens):
		count = 16 if(0 < len(tokens) and tokens[0] == "w") else 8
		stack_peek = self.unicorn.mem_read(self.unicorn.reg_read(UC_X86_REG_RSP) - 8, 100 * 8)
		self.view_stack(self.unicorn.reg_read(UC_X86_REG_RSP) + 100 * 8, pretty_print_bytes(stack_peek, aschii=False), length=count)
	#	print(count)
	#	print(tokens)

	def peek_data(self, tokens):
		print(len(tokens))
		size = tokens[2] if(2 < len(tokens)) else (100 * 8)
		count = 16 if(1 < len(tokens) and tokens[1] == "w") else 8
		location = self.parse_math(tokens[0])

		print("LOL?")
		stack_peek = self.unicorn.mem_read(location, size)
		self.view_stack(location, pretty_print_bytes(stack_peek, aschii=False), length=count)		

		print(count)

	def read_2_null(self, start):
		results = []
		string = []
		while True:
			byte_location = self.unicorn.mem_read(start, 1)
			results.append(byte_location[0])
			string.append(chr(byte_location[0]))
			if(byte_location[0] == 0):
				break
			start += 1
		return bytes(bytearray(results)), "".join(string)

	def read_null_terminated(self, tokens):
		results, string = self.read_2_null(self.parse_math(tokens[0]))
		pretty_print_bytes(bytes(bytearray(results)))

	def db_register_commit(self, tokens):
		name = tokens[0]
		print("Latest commit in {}, was at {}".format(name, hex(self.parrent.get_latest_register_write(name))))
		location = self.parrent.get_latest_register_write(name)
		print("Binary location : {}".format(hex(location-self.parrent.library_offset(location))))

	def print_math(self, tokens):
		results = (self.parse_math(tokens[0]))
		print("0x%x, %i" % (results, results))

	def print_instruction(self, tokens):
		address, size = self.current_address, self.current_size
		instruction_name, hook_instruction, hook_name = self.get_instruction(address, size)
		print(instruction_name)

	def hash_bytes(self, tokens):
		'''
		-	use this to test gdb
import hashlib
i = gdb.inferiors()[0]
m = i.read_memory(0x7ffff7fe6000, 0x11f09)
hash_data = hashlib.sha256()
hash_data.update(m.tobytes())
print(hash_data.hexdigest())
		'''
		if(len(tokens) == 2):
			location = self.parse_math(tokens[0])
			size = self.parse_math(tokens[1])
			hash_data = hashlib.sha256()
			hash_data.update(bytes(self.unicorn.mem_read(location, size)))
			print(hash_data.hexdigest())
		else:
			print("hash_bytes *location* *size*")

	def parse_hex_string(self, tokens):
		if(len(tokens) == 0):
			return
		if(tokens[0] == "big"):
			input_string = "\t".join(tokens[1:])
			hex_2_string(input_string, big=True)

		elif(tokens[0].isalpha()):
			input_string = hex(self.parse_math(tokens[0]))
			hex_2_string(input_string)			
		else:
			input_string = "\t".join(tokens)
			hex_2_string(input_string)
		print("")

	def handle_commands(self, memory_access=False):
		if(memory_access):
			command = input("Memory access hit, write a command or press enter to continue\n")
		else:
			command = input("Breakpoint hit({}), write a command or press enter to continue\n".format(hex(self.current_address)))
		commands = {
			"view":self.get_register,
			"stepi":self.step,
			"x":self.memory_handle,
			"read_2_null":self.read_null_terminated,
			"hex_string":self.parse_hex_string,
			"peek_stack":self.peek_stack,
			"peek":self.peek_data,
			"last_commit":self.db_register_commit,
			"do_math":self.print_math,
			"i":self.print_instruction,
			"branch":self.get_branches,
			"hash_bytes":self.hash_bytes
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
					bold_print("\tlast instruction[0x%x] changed %s	[%s -> %s]" % (self.current_address, name, self.readable_eflags(self.register_state[name]), self.readable_eflags(current_state)))
				else:
					bold_print("\tlast instruction[0x%x] changed %s	[0x%x 0x%x]" % (self.current_address, name, self.register_state[name], current_state))

				if(unicorn_refrence[1] == True):
					input("Paused exec because of changed state\n")
				self.register_state[name] = current_state

	def resolve_hook_instruction(self):
		address, size = self.current_address, self.current_size
		instruction_name, hook_instruction, hook_name = self.get_instruction(address, size)
		if(self.logging):
			print('\t\t%s' % instruction_name)

		if(hook_instruction or self.hook_points.get(hex(address), None) != None):
			if(hook_name == "Memory value"):
				self.handle_commands(memory_access=True)
				return False

			if(self.hook_points.get(hex(address), None) != None):
				hook_name = hex(address)

			spesification = self.hook_points[hook_name][1]
			max_hit_count = spesification.get("max_hit_count", None)

			hooked_RIP = False # don't want to overwrite the hooked instruction pointer
			if(max_hit_count != None):
				current_count = spesification.get("count", 0)
				print("instruction got hooked (%i)" % (current_count))
				if(current_count <= max_hit_count):
					spesification["count"] = current_count + 1
				else:
					if(hook_instruction == False):
						raise Exception("hit max for %s, increase max_count for no Exception" % (hex(address)))
					else:
						raise Exception("hit max for %s, increase max_count for no Exception" % (hook_name))

				change_list = self.hook_points[hook_name][0].get(current_count, None)
				if(change_list == None):
					change_list = self.hook_points[hook_name][0].get(0, None)
					assert type(change_list) == dict, "need to provide default hook"

				for register, value in change_list.items():				
					if("RIP" in register.upper()):
						hooked_RIP = True
					register = eval("UC_X86_REG_{}".format(register.upper()))
					if(type(value) == str):
						register_value = self.unicorn.reg_read(eval("UC_X86_REG_{}".format(value.upper())))
						self.unicorn.reg_write(register, register_value)
					else:
						self.unicorn.reg_write(register, value)
			else:
				print("instruction got hooked")
				for register, value in self.hook_points[hook_name][0].items():				
					if("RIP" in register.upper()):
						hooked_RIP = True
					
					register = eval("UC_X86_REG_{}".format(register.upper()))
					self.unicorn.reg_write(register, value)

			if not hooked_RIP:
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

	def add_adress_trace(self, address, register):
		self.print_at_address[address] = register

	def resolve_break_point(self):
		rip = self.unicorn.reg_read(UC_X86_REG_RIP)
		self.current_breakpoint = self.breakpoints.get(rip, None)

		#for key, value in
		adress_trace = self.print_at_address.get(rip, [])
		if(0 < len(adress_trace)):
			print("Values at 0x%x" % (rip), end=": ")
			for register in adress_trace:
				print("%s == 0x%x" % (register, self.unicorn.reg_read(eval("UC_X86_REG_{}".format(register.upper())))), end=" ")
				try:
					print("[%x]", self.unicorn.mem_read(self.unicorn.reg_read(eval("UC_X86_REG_{}".format(register.upper()))), 8), end=" ")
					print("[%x]", self.unicorn.mem_read(self.unicorn.reg_read(eval("UC_X86_REG_{}".format(register.upper())))-8, 8), end=" ")
				except Exception as e:
#					print(e)
					pass
			print("")

		if(self.current_breakpoint != None or self.next_break):
			self.next_break = False
			if(type(self.current_breakpoint) == str):
				if(self.current_breakpoint == "exit"):
					print("will exit after commands")
					if not self.handle_commands() == "stepi":
						exit(0)
				elif(self.current_breakpoint == "jump"):
					self.unicorn.reg_write(UC_X86_REG_RIP, self.current_address + self.current_size)
				else:
					self.handle_commands()
			elif(type(self.current_breakpoint) == int):
				hit_score = self.breakpoints_hits.get(self.unicorn.reg_read(UC_X86_REG_RIP), 0)
				if(hit_score == self.current_breakpoint):
					print("hit breakpoint enougth times to activate")
					self.handle_commands()
				else:
					self.breakpoints_hits[self.unicorn.reg_read(UC_X86_REG_RIP)] = hit_score + 1
			elif(isfunction(self.current_breakpoint)):
				self.current_breakpoint(self.unicorn)
			else:
				self.handle_commands()

	def jump_op(self, string, patch, custom_code=None):
		'''
			keystone will check for illegal operations!

		'''
		try:
			ks = Ks(KS_ARCH_X86, KS_MODE_64)
			encoding, count = ks.asm(string)
		except KsError as e:
			print("ERROR: %s" %e)	

		self.jump_op_list[string] = [encoding, len(encoding), patch, custom_code]

	def panic_patch(self, address):
		print("Did a panic_patch at 0x%x , okay ? " % (address))
		self.log_2_file(address)
		for key, value in self.patch_values.items():
			self.unicorn.reg_write(eval("UC_X86_REG_{}".format(key.upper())), value)

		self.unicorn.reg_write(UC_X86_REG_RIP, address + self.next_size)
		self.next_size = 0
		self.next_jump = False
		self.patch_values = None
	#	input("")

	def check_illegal_op(self):

		size_blocks = {

		}
		for key, value in self.jump_op_list.items():
			if(size_blocks.get(value[1], None) == None):
				size_blocks[value[1]] = list(self.unicorn.mem_read(self.current_address + self.current_size, value[1]))

			if(value[0] == size_blocks[value[1]]):
				if(value[3] == None):
					self.next_jump = True
					self.next_size = value[1]
					self.patch_values = value[2]
				else:
					value[3]()
	

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

			self.check_illegal_op()
	
			self.instruction_count += 1
	
			if(self.resolve_hook_instruction()):
				#	the instruction did a patch ...
				return None

			self.resolve_break_point()
			
			if(self.max_instructions <= self.instruction_count and not self.non_stop):
				if self.test or not should_continue("hit instruction_count limit, continue?"):
					if(should_continue("open debugger?")):
						self.handle_commands()

					self.unicorn.emu_stop()
					self.log_file.close()
			#		print(self.log_file.closed)
				else:
			#		self.unicorn.emu_stop()
			#		self.log_file.close()
			#		else:
					self.max_instructions *= 2

		except Exception as e:
			print(e)
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			if(self.logging_enabled):
				self.log_file.close()
			raise Exception("error in debugger")

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
				return "{} [{}]".format(location_name, hex(address - address_location[0]))
		return "unknown"

