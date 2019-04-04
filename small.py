from disassemble import *
import sys

def reverse_bytearray(wokring_bytearray):
	new_byte_array = list(wokring_bytearray)
	new_byte_array.reverse()
	new_byte_array = bytearray(new_byte_array)
	return new_byte_array

def int_from_bytearray(input_array):
	return int(input_array.hex(), 16)
	return int(input_array.hex(), 16)

class elf:
	def read_with_offset(self, offset, size, reverse=True):
		if(reverse):
			return reverse_bytearray(self.file[offset:offset + size])
		else:
			return (self.file[offset:offset + size])

	def parse_section(self, start):
		self.name = int_from_bytearray(self.read_with_offset(start, 4))
		self.type = (self.read_with_offset(start + 4, 4))

		if(self.is_64_bit):
			self.flags = (self.read_with_offset(start + 0x8, 8))
		else:
			self.flags = (self.read_with_offset(start + 0x8, 4))

		if(self.is_64_bit):
			self.virtual_address = (hex(int_from_bytearray(self.read_with_offset(start + 0x10, 8))))
			self.offset = int_from_bytearray(self.read_with_offset(start + 0x18, 8))
			self.size = int_from_bytearray(self.read_with_offset(start + 0x20, 8))
		else:
			self.virtual_address = (hex(int_from_bytearray(self.read_with_offset(start + 0x0C, 4))))
			self.offset = int_from_bytearray(self.read_with_offset(start + 0x10, 4))
			self.size = int_from_bytearray(self.read_with_offset(start + 0x14, 4))

		section = {
			"name_index":self.name,
			"type":int_from_bytearray(self.type),
			"flags":int_from_bytearray(self.flags),
			"virtual_address":self.virtual_address,
			"file_offset":self.offset,
			"size":self.size	
		}
		return section

	def read_zero_terminated_string(self, offset):
		string = ""
		index = 0
		while True:
			char = self.read_with_offset(offset + index, 1, reverse=False).decode()
			if(char == '\0'):
				break
			string += char
			index += 1	
		return string

	def get_section_names(self):
		string_table_offset = self.sections[self.section_names]["file_offset"]
		self.sections_with_name = {

		}
		for i in self.sections:
			name = (self.read_zero_terminated_string(string_table_offset + self.sections[i]["name_index"]))
			print(name)
			self.sections_with_name[name] = self.sections[i]
	def __init__(self, name):
		self.file = open(name, "rb").read()

		self.is_64_bit = self.file[0x04] == 2
		self.extra_offset = 0 if not self.is_64_bit else 4

		self.sections = {

		}

		if(self.is_64_bit):
			self.section_start = int_from_bytearray(self.read_with_offset(0x28, 8))
			self.section_size = int_from_bytearray(self.read_with_offset(0x3A, 2))
			self.section_number = int_from_bytearray(self.read_with_offset(0x3C, 2))
			self.section_names = int_from_bytearray(self.read_with_offset(0x3E, 2))
		else:
			self.section_start = int_from_bytearray(self.read_with_offset(0x20, 4))
			self.section_size = int_from_bytearray(self.read_with_offset(0x2E, 2))
			self.section_number = int_from_bytearray(self.read_with_offset(0x30, 2))
			self.section_names = int_from_bytearray(self.read_with_offset(0x32, 2))
		
		for i in range(self.section_number):
			self.sections[i] = self.parse_section(self.section_start + self.section_size * i)
		
		self.get_section_names()

		text_seciton = self.sections_with_name[".text"]
		text_content = self.read_with_offset(text_seciton["file_offset"], text_seciton["size"], False)
		decompile(text_content, int(text_seciton["virtual_address"].replace("0x", ""), 16), self.is_64_bit)

		self.start_program_header = self.file[0x18: 0x18 + 4 + self.extra_offset]
		self.start_program_header = reverse_bytearray(self.start_program_header)
		self.start_program_header = int_from_bytearray(self.start_program_header)
if __name__ == "__main__":
	if(len(sys.argv) > 1):
		elf(sys.argv[1])
	else:
		print("scripy.py elf-binary")

