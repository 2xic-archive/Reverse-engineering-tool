
from unicorn.x86_const import *

class memory_mapper(object):
	def __init__(self):
		self.base_program_address = 0x400000
		self.stack_address = None
		self.stack_size = 1024 * 1024 * 4

		self.address_space = {

		}
		self.map_binary()
		self.map_stack()
		self.map_page_zero()
		'''
			* Dynamic mapping will happen here *
				-	already coded part of the linker
				-	will have a static binary running before more work on dynamic (done, sonn dynamic)
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


		self.emulator.mem_map(location, size)
	#	print((location, size))

		if not memory_bytes == None:
			self.emulator.mem_write(location, memory_bytes)

		self.address_space[name] = [location, location + size]

	def load_binary_sections_small(self):
		self.brk = 0x6b6000

		self.section_virtual_map = {
			
		}

		self.section_map = {
			
		}
		mappings = []
		low_address = 0x0
		high_address = 0x0

		for name, content in (self.target.program_headers).items():
			if(content["type_name"] == "PT_NULL"):
				continue
			
			file_offset = content["location"]
			file_end = file_offset + int(content["size"])
			section_bytes = self.target.file[file_offset:file_end]

			start = int(content["virtual_address"], 16)
			end = int(content["virtual_address"], 16) + int(content["size"])

			low_address = min(low_address, start)
			high_address = max(high_address, end)
		
			mappings.append([self.base_program_address + content["location"], section_bytes])


		for name, content in (self.target.sections_with_name).items():
			self.section_map[name] = [ int(content["virtual_address"],16),  int(content["virtual_address"],16) + content["size"]]

			if(content["type_name"] == "SHT_NOBITS" or not "SHF_ALLOC" in content["flags"]):
				self.log_text("Skipped section %s (%s)" % (name, content["flags"]))
				continue

			if("SHF_WRITE" in content["flags"]):
				new_address = int(content["virtual_address"],16) + int(content["size"])
		#		if(self.brk < new_address):
		#			self.brk = new_address

			file_offset = content["file_offset"]
			file_end = file_offset + int(content["size"])
			section_bytes = self.target.file[file_offset:file_end]

			start = int(content["virtual_address"],16)
			end = int(content["virtual_address"],16) + int(content["size"])

			low_address = min(low_address, start)
			high_address = max(high_address, end)
			self.log_text("Loaded section %s at 0x%x -> 0x%x (%s)" % (name, start, end, content["flags"]))

			mappings.append([int(content["virtual_address"],16), section_bytes])

			if(content["size"] > 0):
				self.section_virtual_map[name] = [start, end]	
		return mappings, low_address, high_address

	def map_binary(self):
		mappings, low_address, high_address = self.load_binary_sections_small()
		self.program_size = self.round_memory(high_address - low_address)

		print(hex(self.base_program_address))
		print(hex(self.program_size))

		self.map_target(self.base_program_address, self.program_size, None, "program")

		for secition in mappings:
			self.emulator.mem_write(secition[0], secition[1])

	def map_stack(self):
		if(self.stack_address == None):
			self.stack_address = self.round_memory(self.base_program_address + self.program_size + 64)

		self.map_target(self.stack_address, self.stack_size, None, "stack")
#		self.emulator.mem_map(stack_adr, stack_size)
		self.emulator.reg_write(UC_X86_REG_RSP, self.stack_address + self.stack_size - 1)


	def map_page_zero(self):
		self.map_target(0, self.base_program_address, None, "paze zero")

