
from unicorn.x86_const import *
from .dynamic_linker import *
from elf.elf_parser import *
class memory_mapper(object):
	def __init__(self):
		self.base_program_address = self.target.base_address #0x400000

		self.stack_address = None
		self.stack_size = 1024 * 1024 * 4
		self.current_library_address = 0x900000

		self.address_space = {

		}
		self.map_binary()
		self.map_stack()
		self.map_page_zero()

		if not self.target.static_binary:
			self.map_library()

		'''
			* Dynamic mapping will happen here *
				-	already coded part of the linker
				-	will have a static binary running before more work on dynamic (done, sonn dynamic)
		'''

	def map_library(self):
		'''
			PSA : just realized that libc is depended on ld. I thought the binary would list ld
			as a consequence, but when I ran readelf -d /lib/x86_64-linux-gnu/libc-2.24.so | grep NEEDED
			and now I understand!

			-	will have to redo the structure below....
			for each library get the needed parrent libraries.
		'''
		libraries = [elf("/lib/x86_64-linux-gnu/libc.so.6"),
					 elf("/lib/x86_64-linux-gnu/ld-2.24.so")]

#		link_lib_and_binary(libraries[0], libraries[1])
#		exit(0)

		for library in libraries:
			print("round two")
			mappings, low_address, high_address = self.load_binary_sections_small(library, self.current_library_address)
			library_size = self.round_memory((high_address - low_address) + 1)
			self.map_target(self.current_library_address, library_size, None, "library")

			for secition in mappings:
				if(self.is_memory_mapped(secition[0] + len(secition[1]))):
					self.emulator.mem_write(secition[0], secition[1])
				else:
					start = self.round_memory(secition[0])
					self.map_target(start,  self.round_memory(len(secition[1])), secition[1], "section ?")
			
			for i in link_lib_and_binary(self.target, library):
				unicorn_base = int(i[0], 16)
				library_map, library_map_size = i[1]
				library_map = int(library_map, 16)
				library_map += self.current_library_address

				new_address = bytes(bytearray(struct.pack("<Q", library_map)))
				self.emulator.mem_write(unicorn_base, new_address)

			self.current_library_address +=  self.round_memory((library_size) + 1)

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

	def load_binary_sections_small(self, binary, offset):
		self.brk = 0 # 0x6b6000

		self.section_virtual_map = {
			
		}

		self.section_map = {
			
		}
		mappings = []
		low_address = 0x0
		high_address = 0x0

		for name, content in (binary.program_headers).items():
			if(content["type_name"] == "PT_NULL"):
				continue
			
			file_offset = content["location"]
			file_end = file_offset + int(content["size"])
			section_bytes = binary.file[file_offset:file_end]

			start = int(content["virtual_address"], 16)
			end = int(content["virtual_address"], 16) + int(content["size"])

			low_address = min(low_address, start)
			high_address = max(high_address, end)
		
			mappings.append([offset + content["location"], section_bytes])


		for name, content in (binary.sections_with_name).items():
			self.section_map[name] = [ int(content["virtual_address"],16),  int(content["virtual_address"],16) + content["size"]]

			if(content["type_name"] == "SHT_NOBITS" or not "SHF_ALLOC" in content["flags"]):
				self.log_text("Skipped section %s (%s)" % (name, content["flags"]))
				continue

			if("SHF_WRITE" in content["flags"]):
				new_address = int(content["virtual_address"],16) + int(content["size"])
				if(self.brk < new_address):
					self.brk = new_address

			file_offset = content["file_offset"]
			file_end = file_offset + int(content["size"])
			section_bytes = binary.file[file_offset:file_end]

			start = int(content["virtual_address"],16)
			end = int(content["virtual_address"],16) + int(content["size"])

			low_address = min(low_address, start)
			high_address = max(high_address, end)
			self.log_text("Loaded section %s at 0x%x -> 0x%x (%s)" % (name, start, end, content["flags"]))

			mappings.append([offset + int(content["virtual_address"],16), section_bytes])

			if(content["size"] > 0):
				self.section_virtual_map[name] = [start, end]	
		return mappings, low_address, high_address

	def map_binary(self):
		mappings, low_address, high_address = self.load_binary_sections_small(self.target, self.base_program_address)
		self.program_size = self.round_memory((high_address - low_address) + 1)
		self.map_target(self.base_program_address, self.program_size, None, "program")

		for secition in mappings:
			if(self.is_memory_mapped(secition[0] + len(secition[1]))):
				self.emulator.mem_write(secition[0], secition[1])
			else:
				start = self.round_memory(secition[0])
				self.map_target(start,  self.round_memory(len(secition[1])), secition[1], "section ? ")


	def map_stack(self):
		if(self.stack_address == None):
			self.stack_address = self.round_memory(self.base_program_address + self.program_size + 64)

		self.map_target(self.stack_address, self.stack_size, None, "stack")
#		self.emulator.mem_map(stack_adr, stack_size)
		self.emulator.reg_write(UC_X86_REG_RSP, self.stack_address + self.stack_size - 1)

	def is_memory_mapped(self, address):
		for memory_name in self.address_space.keys():
			memory_window = self.address_space[memory_name]
#			print(memory_name)
#			print(((memory_window[0], address, memory_window[1])))
			if(memory_window[0] <= address <= memory_window[1]):
				return True
		return False

	def map_page_zero(self):
		if(self.base_program_address == 0):
			print("Probably loaded a dynamic binary. Page zero should be remapped.")
		else:
			self.map_target(0, self.base_program_address, None, "paze zero")

