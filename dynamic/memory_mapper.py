
from unicorn.x86_const import *
from .dynamic_linker import *
from elf.elf_parser import *

class memory_mapper(object):
	def __init__(self):
		self.base_program_address = self.target.base_address #0x400000


		if(self.base_program_address == 0):
			self.base_program_address = 0x200000

		self.stack_address = None
		self.stack_size = 1024 * 1024 * 4
		self.current_library_address = 0x900000
		self.msr_location = 0xf00000

		self.address_space = {

		}
		self.map_binary()
		self.map_stack()
		self.map_page_zero()

		if not self.target.static_binary:
			self.map_library()
	#		print(hex(0xca244d-self.look_up_library["ld-linux-x86-64.so.2"][0]))
	#		exit(0)
#			self.boot_ld()


#			print(self.look_up_library)
#			input("run ? ")
#			self.run_library_test()
	'''
		should help with detecting bugs in linker.
	'''
	def write_illegal_library(self, location):
		current_written_address = self.emulator.mem_read(location, 8)
		if(int.from_bytes(current_written_address, byteorder='little') == 0):
			#self.emulator.mem_write(location, bytes(bytearray(struct.pack("<Q", 0xf00dbeef))))
			pass

	def read_qword(self, start):
		address_bytes = self.emulator.mem_read(start, 8)
		address_hex = hex(int.from_bytes(address_bytes, byteorder='little'))
		return [address_bytes, list(address_bytes) , address_hex]

	def run_library_test(self):
#		print(self.look_up_library)
		for x in [[0x224f48, "ld-linux-x86-64.so.2"]]:
			target = self.look_up_library[x[1]][0] + x[0]#1465824
			print(x)
			print(self.read_qword(target))
			print(self.written_addresses.get(target, None))
			print("")
		#	0x397240
		exit(0)

	def boot_ld(self):
		'''
			need to run the linux dynamic linker
			http://man7.org/linux/man-pages/man8/ld.so.8.html			
		'''
#		print(self.look_up_library)
#		input("run?")
		self.run_binary(program_entry_point=self.look_up_library["ld-linux-x86-64.so.2"][0] + self.look_up_library["ld-linux-x86-64.so.2"][2].program_entry_point)
#		self.run(program_entry_point=libraries[libraries.index("ld-linux-x86-64.so.2")].program_entry_point)
		#	program_entry_point
#		exit(0)
#		print(self.emulator.mem_read(0xca1ad5+0x222394, 8))
#		print(self.emulator.mem_read(0xca1ad5+0x222394+8, 8))
#		input("need to run binary ? ")
		
	def map_library(self):
		self.look_up_library = {

		}

		self.written_addresses = {

		}

		'''
			reading in all libraries used by the binary and the libs.
		'''
		libraries = []
		for i in get_needed_libraries(self.target):
			libraries.append(elf("/lib/x86_64-linux-gnu/" + i))

		index = 0
		while(index < len(libraries)):
			lib = libraries[index]
			for j in get_needed_libraries(lib):
				if not "/lib/x86_64-linux-gnu/" + j in libraries:
					libraries.append(elf("/lib/x86_64-linux-gnu/" + j))
			index += 1

		for library in libraries:
			mappings, low_address, high_address = self.load_binary_sections_small(library, self.current_library_address)
			library_size = self.round_memory((high_address - library.base_address) + 1)
			self.map_target(self.current_library_address, library_size, None, "library [{}]".format(library.file_name))

			for secition in mappings:
				self.emulator.mem_write(secition[0], secition[1])

			self.look_up_library[library.file_name] = [self.current_library_address, library_size, library]

			for i in link_lib_and_binary(self.target, library):
				binary = int(i[0], 16)
				binary += (self.base_program_address)

				if(i[1] == "DIRECT_MAPPING_"):
					library_map = i[2]
					library_map += self.base_program_address
				else:				
					library_map, library_map_size = i[1]
					library_map = int(library_map, 16)
					library_map += self.current_library_address

				xref = bytes(bytearray(struct.pack("<Q", library_map)))

				if(i[1][0] == "0xf00dbeef"):
					self.write_illegal_library(binary)
				else:
					self.emulator.mem_write(binary, xref)
					self.written_addresses[binary] = self.written_addresses.get(binary, 0) + 1

			self.current_library_address += self.round_memory((library_size) + 1)

		for lib in libraries:
			for needed_lib in get_needed_libraries(lib):
				dependent_library = libraries[libraries.index("/lib/x86_64-linux-gnu/" + needed_lib)]
				for i in link_lib_and_binary(lib, dependent_library):
					parrent_library = int(i[0], 16)
					parrent_library += self.look_up_library[lib.file_name][0]

					if(i[1] == "DIRECT_MAPPING_"):
						children_library = i[2]
						children_library += self.look_up_library[lib.file_name][0]
					else:						
						children_library, library_map_size = i[1]
						children_library = int(children_library, 16)
						children_library += self.look_up_library[dependent_library.file_name][0]

					if(i[1][0] == "0xf00dbeef"):
						self.write_illegal_library(binary)
					else:
						xref = bytes(bytearray(struct.pack("<Q", children_library)))
						self.emulator.mem_write(parrent_library, xref)
						self.written_addresses[parrent_library] = self.written_addresses.get(parrent_library, 0) + 1

				for i in link_lib_and_binary(dependent_library, None):
					if(i[1] == "DIRECT_MAPPING_"):
						parrent_map = int(i[0], 16)
						parrent_map += self.look_up_library[dependent_library.file_name][0]

						child_map = i[2]
						child_map += self.look_up_library[dependent_library.file_name][0]
						xref = bytes(bytearray(struct.pack("<Q", child_map)))
							
						self.emulator.mem_write(parrent_map, xref)
						self.written_addresses[parrent_map] = self.written_addresses.get(parrent_library, 0) + 1
#		print(self.look_up_library)

#		self.future_breakpoints.append(0x1860 + self.look_up_library["ld-linux-x86-64.so.2"][0])
#		self.future_breakpoints.append(0xc20 + self.look_up_library["libc.so.6"][0])
#		self.future_breakpoints.append(0x20400 + self.look_up_library["libc.so.6"][0])

#		self.future_breakpoints.append(self.look_up_library["ld-linux-x86-64.so.2"][0] + 0x2481)
#		self.future_breakpoints.append(self.look_up_library["ld-linux-x86-64.so.2"][0] + 0x2493)

	def resolve_dynamic_setup(self):
		# this is only for a dynamic binary
		if self.target.static_binary:
			return None
		'''
			based on some looks in gdb and hopper rdx should point to
			lib_ld + 0xfba0 (_dl_fini), not sure why it is not named in the binary tho.
		'''
		
#		self.emulator.reg_write(UC_X86_REG_RDX, self.look_up_library["ld-linux-x86-64.so.2"][0] + 0xfba0)

		'''	
			-	this should be fixed with a linker update?
		'''
		'''
		self.emulator.mem_write(self.look_up_library["libc.so.6"][0] + 0x399000, 
			bytes(bytearray(struct.pack("<Q", self.look_up_library["ld-linux-x86-64.so.2"][0] + 0x224040))))

		self.emulator.mem_write(self.look_up_library["libc.so.6"][0] + 0x398df1, 
			bytes(bytearray(struct.pack("<Q", self.look_up_library["ld-linux-x86-64.so.2"][0] + 0x224040))))

		self.emulator.mem_write(self.look_up_library["libc.so.6"][0] + 0x398df8, 
			bytes(bytearray(struct.pack("<Q", self.look_up_library["ld-linux-x86-64.so.2"][0] + 0x224040))))
		'''

	# unicorn want size adn adress to be 4KB aligned
	def round_memory(self, offset):
		return (offset + ((4 * 1024 - 1))) & ~((4 * 1024 - 1))

	def check_legal_size(self, size):
		return ((size & (4*1024 - 1)) == 0)

	def map_target(self, location, size, memory_bytes, name):
		if not self.check_legal_size(location):
			raise Exception("illegal map location, need to be 4kb aligned")
		if not self.check_legal_size(size):
			raise Exception("illegal map size, need to be 4kb aligned")
		if self.is_memory_mapped(location):
			raise Exception("this memory is already mapped?")

		self.emulator.mem_map(location, size)
	#	print((location, size))

		if not memory_bytes == None:
			self.emulator.mem_write(location, memory_bytes)

		self.address_space[name] = [location, location + size]

	def extend_bytearray(self, array_input, size):
		while(len(array_input) < size):
			array_input.append(0)
		return array_input

	def load_binary_sections_small(self, binary, offset):
		self.brk = 0 # 0x6b6000

		self.section_virtual_map = {
			
		}

		self.section_map = {
			
		}
		mappings = []
		low_address = 0x0
		high_address = 0x0

		mappings.append([offset, bytes(binary.file_header), "fileheader {}".format(binary.file_name)])

		for name, content in (binary.program_headers).items():
#			if(content["type_name"] == "PT_NULL"):
#				continue
			
			file_offset = content["location"]
			file_end = file_offset + int(content["size"])
			section_bytes = binary.file[file_offset:file_end]

			start = int(content["virtual_address"], 16)
			end = start + int(content["size"])

			low_address = min(low_address, start)
			high_address = max(high_address, end)
		
			assert(len(section_bytes) == int(content["size"]))

			mappings.append([offset + content["location"], section_bytes, name])

			if((offset + content["location"]) < 0x40):
				print(("[%s]Loaded section %s at 0x%x -> 0x%x (%s)" % (binary.file_name, name, start, end, content["flags"])))


		for name, content in (binary.sections_with_name).items():
			self.section_map[name] = [ int(content["virtual_address"],16),  int(content["virtual_address"],16) + content["size"]]


#			if not "SHF_ALLOC" in content["flags"]:
#				self.log_text("Skipped section %s (%s)" % (name, content["flags"]))
#				continue

			if(int(content["virtual_address"], 16) == 0):
				'''
				sh_addr
					If the section is to appear in the memory image of a process, 
					this member gives the address at which the section's first byte should reside. 
					Otherwise, the member contains 0.
				-	https://docs.oracle.com/cd/E19683-01/817-3677/chapter6-94076/index.html
				'''
				continue

			'''
				brk should only get adjusted on the target binary ?
				- not sure about the libs.
			'''
			if("SHF_WRITE" in content["flags"]):
				new_address = int(content["virtual_address"],16) + int(content["size"])
				if(self.brk < new_address):
					self.brk = new_address

		#		continue

			file_offset = content["file_offset"]
			file_end = file_offset + int(content["size"])
			
			section_bytes = bytes()
			if not (content["type_name"] == "SHT_NOBITS"):
				section_bytes = binary.file[file_offset:file_end]

			start = int(content["virtual_address"],16)
			end = start + int(content["size"])

			low_address = min(low_address, start)
			high_address = max(high_address, end)
		
			if((offset + start) < 0x40):
				print(("SHF_ALLOC" in content["flags"]))
				print(("[%s]Loaded section %s at 0x%x -> 0x%x (%s)" % (binary.file_name, name, start, end, content["flags"])))
				print(int(content["size"]) == len(bytearray(section_bytes)))

			self.log_text("Loaded section %s at 0x%x -> 0x%x (%s)" % (name, start, end, content["flags"]))

			section_bytes = bytes(self.extend_bytearray(bytearray(section_bytes), int(content["size"])))

			assert(len(section_bytes) == int(content["size"]))
			mappings.append([offset + start, section_bytes, name])

			if(content["size"] > 0):
				self.section_virtual_map[name] = [start, end]	
		return mappings, low_address, high_address

	def map_binary(self):
		mappings, low_address, high_address = self.load_binary_sections_small(self.target, self.base_program_address)
		self.program_size = self.round_memory((high_address - low_address) + 1)
		self.map_target(self.base_program_address, self.program_size, None, "program")

		for secition in mappings:
			self.emulator.mem_write(secition[0], secition[1])


	def map_stack(self):
		if(self.stack_address == None):
			self.stack_address = self.round_memory(self.base_program_address + self.program_size + 64)

		self.map_target(self.stack_address, self.stack_size, None, "stack")
#		self.emulator.mem_map(stack_adr, stack_size)
		self.emulator.reg_write(UC_X86_REG_RSP, self.stack_address + self.stack_size - 1)

	def library_offset(self, address):
#		print(self.look_up_library)
		for name, value in self.look_up_library.items():
	#		print((value[0]) , address)
	#		print((address , value[0] + value[1]))
			if((value[0]) <= address <= (value[0] + value[1])):
				return value[0]
		return address

	def is_memory_mapped(self, address):
		'''
			TODO : binary search here
		'''
		for memory_name in self.address_space.keys():
			memory_window = self.address_space[memory_name]
#			print(memory_name)
#			print(((memory_window[0], address, memory_window[1])))
			if(memory_window[0] <= address <= memory_window[1]):
				return True
		return False

	def map_page_zero(self):
		self.map_target(self.msr_location, self.round_memory(8), None, "msr location")
		if(self.base_program_address == 0 or not self.target.static_binary):
			print("Probably loaded a dynamic binary. Page zero should be remapped.")
			self.map_target(0, self.base_program_address, None, "paze zero")
		else:
			self.map_target(0, self.base_program_address, None, "paze zero")

