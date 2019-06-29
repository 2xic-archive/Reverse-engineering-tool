import sys
from static.disassemble import *
#from elf_parser_key_value import *
from .elf_parser_key_value import *
from dynamic.dynamic_linker import *
from collections import OrderedDict
import os

def reverse_bytearray(wokring_bytearray):
	new_byte_array = list(wokring_bytearray)
	new_byte_array.reverse()
	new_byte_array = bytearray(new_byte_array)
	return new_byte_array

def int_from_bytearray(input_array):
	return int(input_array.hex(), 16)

def int_to_bytearray(input_int, size):
	some_bytes = input_int.to_bytes(size, sys.byteorder)
	return bytearray(some_bytes)


class elf:
	def read_with_offset(self, offset, size, reverse=True):
		if(reverse):
			return reverse_bytearray(self.file[offset:offset + size])
		else:
			return (self.file[offset:offset + size])

	def write_with_offset(self, offset, input_bytes, custom=None):
		if(type(self.file) != bytearray):
			self.file = bytearray(self.file)
		self.file[offset:offset+len(input_bytes)] = input_bytes
			
	def parse_section_header(self, start):
		section_name = int_from_bytearray(self.read_with_offset(start, 4))
		section_type = (self.read_with_offset(start + 4, 4))

		if(self.is_64_bit):
			section_flags = (self.read_with_offset(start + 0x8, 8))
		else:
			section_flags = (self.read_with_offset(start + 0x8, 4))

		if(self.is_64_bit):
			section_virtual_address = (hex(int_from_bytearray(self.read_with_offset(start + 0x10, 8))))
			section_file_offset = int_from_bytearray(self.read_with_offset(start + 0x18, 8))
			section_size = int_from_bytearray(self.read_with_offset(start + 0x20, 8))

			entries_size =  int_from_bytearray(self.read_with_offset(start + 0x38, 4))
			section_link = int_from_bytearray(self.read_with_offset(start + 0x28, 4))
		else:
			section_virtual_address = (hex(int_from_bytearray(self.read_with_offset(start + 0x0C, 4))))
			section_file_offset = int_from_bytearray(self.read_with_offset(start + 0x10, 4))
			section_size = int_from_bytearray(self.read_with_offset(start + 0x14, 4))
			entries_size = int_from_bytearray(self.read_with_offset(start + 0x24, 4))

			section_link = int_from_bytearray(self.read_with_offset(start + 0x18, 4))

		if(int_from_bytearray(section_type) < 0x60000000):
			type_name = section_type_name[int_from_bytearray(section_type)]
		else:
			type_name = "OS-specific."

		section = {
			"section_location":start,
			"orginal_size":self.read_with_offset(start + 0x20, 8),
			"name_index":section_name,
			"type":int_from_bytearray(section_type),
			"type_name":type_name,
			"flags":get_readable_flags(int_from_bytearray(section_flags)),
			"flags_int":int_from_bytearray(section_flags),
			"section_link":section_link,
			"entries_size":entries_size,
			"virtual_address":section_virtual_address,
			"file_offset":section_file_offset,
			"size":section_size	
		}
		return section

	def parse_program_header(self, start):
		program_header_type = int_from_bytearray(self.read_with_offset(start, 4))
		if(self.is_64_bit):
			program_header_flags = int_from_bytearray(self.read_with_offset(start + 0x04, 4))
			program_header_offset = int_from_bytearray(self.read_with_offset(start + 0x08, 8))
			program_header_viritual_address = int_from_bytearray(self.read_with_offset(start + 0x10, 8))
			program_header_physcial_address = int_from_bytearray(self.read_with_offset(start + 0x18, 8))
			program_header_size_file = int_from_bytearray(self.read_with_offset(start + 0x20, 8))
			program_header_size_memory = int_from_bytearray(self.read_with_offset(start + 0x20, 8))
			program_header_align = int_from_bytearray(self.read_with_offset(start + 0x30, 8))
		else:		
			program_header_offset = int_from_bytearray(self.read_with_offset(start + 0x04, 4))
			program_header_viritual_address = int_from_bytearray(self.read_with_offset(start + 0x08, 4))
			program_header_physcial_address = int_from_bytearray(self.read_with_offset(start + 0x0C, 4))
			program_header_size_file = int_from_bytearray(self.read_with_offset(start + 0x10, 4))
			program_header_size_memory = int_from_bytearray(self.read_with_offset(start + 0x14, 4))
			program_header_flags = int_from_bytearray(self.read_with_offset(start + 0x18, 4))
			program_header_align = int_from_bytearray(self.read_with_offset(start + 0x1C, 4))

		if(0x60000000 < program_header_type < 0x7FFFFFFF):
			name = "reserved for os"
		else:
			name = program_header_type_name.get(program_header_type, "UNKOWN")


#		print(program_header_type)
		if(program_header_type == 0x00000001 and self.base_address != None):
			self.base_address = program_header_viritual_address
#			print(hex(program_header_viritual_address))
		
		if(self.static_binary and name == "PT_INTERP"):
			self.static_binary = False

		return {
			"type":program_header_type,
			"type_name":name,
			"virtual_address":program_header_viritual_address,
			"file_offset":program_header_offset,
			"file_size":program_header_size_file,
			"location":start
		}


	def read_zero_terminated_string(self, offset):
		string = ""
		index = 0
		while (offset + index) < len(self.file):
			char = self.read_with_offset(offset + index, 1, reverse=False).decode()
			if(char == '\0'):
				break
			string += char
			index += 1	
		return string


	def get_section_name_by_index(self, index):
		string_table_offset = self.section_headers[self.section_headers_names]["file_offset"]
		return self.read_zero_terminated_string(string_table_offset + self.section_headers[index]["name_index"])

	def get_section_names(self):
		string_table_offset = self.section_headers[self.section_headers_names]["file_offset"]
		self.sections_with_name = OrderedDict()

		self.sections_with_name_index = OrderedDict()

		self.section_sizes = OrderedDict()
		un_named_count = 0
		for i in self.section_headers:
			name = self.read_zero_terminated_string(string_table_offset + self.section_headers[i]["name_index"])
			if(len(name) == 0):
				name = "unnamed_%i" % (un_named_count)
				un_named_count += 1
			self.sections_with_name[name] = self.section_headers[i]
			self.sections_with_name_index[i] = name
			self.section_sizes[name] = [self.section_headers[i]["file_offset"], self.section_headers[i]["size"]] 
		self.section_sizes["base_address"] = self.base_address

	def read_section(self, key):
		section = self.sections_with_name[key]
		return self.read_with_offset(section["file_offset"], section["size"], False), int(section["virtual_address"].replace("0x", ""), 16)

	def read_section_bytes(self, key):
		section = self.sections_with_name[key]
		location = int(section["virtual_address"].replace("0x", ""), 16)
		fake_index = 0

		range_bytes = OrderedDict()
		for j in range(section["file_offset"], section["file_offset"] + section["size"]):
			range_bytes[hex(location + fake_index)] = [hex(self.file[j]), chr(self.file[j]), []]
			fake_index += 1
		return range_bytes

	def get_sections_parsed(self):
		code_sections = OrderedDict()
		for index, key in self.sections_with_name_index.items(): #enumerate(self.sections_with_name.keys()):
			text_seciton = self.sections_with_name[key]
			
			if(text_seciton["type"] == 0x1 and text_seciton["flags_int"] == 0x6):
				code_sections[index] = key
			else:
				pass
		self.code_sections = code_sections
		return code_sections


	
	def reconstruct_small(self, section, input_bytes):
		readjust_section = [

		]
	
		delta = len(bytearray(input_bytes)) - self.sections_with_name[section]["size"]

		#	need to re-adjust all effected sections.
		for key in self.sections_with_name.keys():
			#	only need to adjust the sections after the changed section
			if(self.sections_with_name[section]["file_offset"] <= self.sections_with_name[key]["file_offset"]):
				readjust_section.append(key)
				print("{}	{}	{}".format(self.sections_with_name[key]["file_offset"], self.sections_with_name[key]["size"], self.sections_with_name[key]["file_offset"] + self.sections_with_name[key]["size"]))
		'''
		new_section = bytearray(self.sections_with_name[section]["size"])
		new_section[:len(input_bytes)] = input_bytes
		results = int_to_bytearray(len(input_bytes), 8)

		self.write_with_offset(self.sections_with_name[section]["section_location"] + 0x20, results)
		self.write_with_offset(self.sections_with_name[section]["file_offset"], new_section)
		open("test_patch", "wb").write(self.file)
		'''

	def is_static(self):
		return self.static_binary

	def load_relocation(self):
		for section_key, section_info in self.sections_with_name.items():
			if(section_info["type"] == 0x4):
				parse_relocation(self, section_key)

	def parse_dynamic_symbol_table(self):
		for section_key, section_info in self.sections_with_name.items():
			if(section_info["type"] == 0x0B):
				get_dynamic_symbols(self, section_key)

	def __init__(self, name):
		self.file = open(name, "rb").read()
		self.file_path = os.path.abspath(name)

		self.is_elf = self.file[:4] == b'\x7fELF'
		assert self.is_elf, "not a elf binary"

		self.is_64_bit = self.file[0x04] == 2
		self.extra_offset = 0 if not self.is_64_bit else 4
		self.base_address = None

		self.static_binary = True

		self.section_headers = OrderedDict()
		self.program_headers = OrderedDict()
		self.symbol_table = OrderedDict()
		self.qword_helper = OrderedDict()

		self.target_architecture_int = int_from_bytearray(self.read_with_offset(0x12, 2))
		self.target_architecture = target_architecture_lookup[self.target_architecture_int]

		if(self.is_64_bit):
			self.program_entry_point = int_from_bytearray(self.read_with_offset(0x18, 8))

			self.program_header_start = int_from_bytearray(self.read_with_offset(0x20, 8))
			self.program_header_count = int_from_bytearray(self.read_with_offset(0x38, 2))
			self.program_header_size = int_from_bytearray(self.read_with_offset(0x36, 2))

			self.section_headers_start = int_from_bytearray(self.read_with_offset(0x28, 8))
			self.section_headers_size = int_from_bytearray(self.read_with_offset(0x3A, 2))
			self.section_headers_count = int_from_bytearray(self.read_with_offset(0x3C, 2))
			self.section_headers_names = int_from_bytearray(self.read_with_offset(0x3E, 2))		

			self.file_header_size = int_from_bytearray(self.read_with_offset(0x34, 2))

		else:
			self.program_entry_point = int_from_bytearray(self.read_with_offset(0x18, 4))

			self.program_header_start = int_from_bytearray(self.read_with_offset(0x1C, 4))
			self.program_header_count = int_from_bytearray(self.read_with_offset(0x2C, 2))
			self.program_header_size = int_from_bytearray(self.read_with_offset(0x2A, 2))

			self.section_headers_start = int_from_bytearray(self.read_with_offset(0x20, 4))
			self.section_headers_size = int_from_bytearray(self.read_with_offset(0x2E, 2))
			self.section_headers_count = int_from_bytearray(self.read_with_offset(0x30, 2))
			self.section_headers_names = int_from_bytearray(self.read_with_offset(0x32, 2))

			self.file_header_size = int_from_bytearray(self.read_with_offset(0x28, 2))


		self.file_header = self.file[:self.file_header_size]		

		for i in range(self.section_headers_count):
			self.section_headers[i] = self.parse_section_header(self.section_headers_start + self.section_headers_size * i)
		
		for i in range(self.program_header_count):
			self.program_headers[i] = self.parse_program_header(self.program_header_start + self.program_header_size * i)

		assert self.program_header_start < self.section_headers_start


		self.get_section_names()

		if not self.is_static():
			self.parse_dynamic_symbol_table()
			self.load_relocation()


if __name__ == "__main__":
	elf(sys.argv[1])


