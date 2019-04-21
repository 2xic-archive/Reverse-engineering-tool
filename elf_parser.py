import sys
from disassemble import *
from elf_parser_key_value import *

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
	#		print(self.read_with_offset(start + 0x8, 8))
	#		exit(0)
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


		section_type_name = {
			0x0:"SHT_NULL",
			0x1:"SHT_PROGBITS",
			0x2:"SHT_SYMTAB",
			0x3:"SHT_STRTAB",
			0x4:"SHT_RELA",
			0x5:"SHT_HASH",
			0x6:"SHT_DYNAMIC",
			0x7:"SHT_NOTE",
			0x8:"SHT_NOBITS",
			0x9:"SHT_REL",
			0x0A:"SHT_SHLIB",
			0x0B:"SHT_DYNSYM",
			0x0E:"SHT_INIT_ARRAY",
			0x0F:"SHT_FINI_ARRAY",
			0x10:"SHT_PREINIT_ARRAY",
			0x11:"SHT_GROUP",
			0x12:"SHT_SYMTAB_SHNDX",
			0x13:"SHT_NUM",
			0x60000000:"SHT_LOOS"
		}

		type_name = "NULL"
		try:
			type_name = section_type_name[int_from_bytearray(section_type)]
		except Exception as e:
			pass


		section = {
			"section_location":start,
			"orginal_size":self.read_with_offset(start + 0x20, 8),
			"name_index":section_name,
			"type":int_from_bytearray(section_type),
			"type_name":type_name,
			"flags":int_from_bytearray(section_flags),
			"section_link":section_link,
			"entries_size":entries_size,
			"virtual_address":section_virtual_address,
			"file_offset":section_file_offset,
			"size":section_size	
		}
		return section

	def parse_program_header(self, start):

		program_header_type_name = {
			0x00000000:"PT_NULL",
			0x00000001:"PT_LOAD",
			0x00000002:"PT_DYNAMIC",
			0x00000003:"PT_INTERP",
			0x00000004:"PT_NOTE",
			0x00000005:"PT_SHLIB",
			0x00000006:"PT_PHDR",
			0x60000000:"PT_LOOS",
			0x6FFFFFFF:"PT_HIOS",
			0x70000000:"PT_LOPROC",
			0x7FFFFFFF:"PT_HIPROC"
		}

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

		name = "NULL"
		try:
			name = program_header_type_name[program_header_type]
		except Exception as e:
			pass
		return {
			"type":program_header_type,
			"type_name":name,
			"file_offset":program_header_offset,
			"file_size":program_header_size_file
		}


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
		string_table_offset = self.section_headers[self.section_headers_names]["file_offset"]
		self.sections_with_name = {

		}
		for i in self.section_headers:
			name = self.read_zero_terminated_string(string_table_offset + self.section_headers[i]["name_index"])
			self.sections_with_name[name] = self.section_headers[i]


	def decompile_section(self, section_name):
		text_seciton = self.sections_with_name[section_name]
		capstone_mode = get_capstone_mode(self.target_architecture, self.is_64_bit)
	#	print(self.target_architecture)
		if(text_seciton["type"] == 0x1 and text_seciton["flags"] == 0x6):
			text_content = self.read_with_offset(text_seciton["file_offset"], text_seciton["size"], False)
			decompiled, registered_touched = decompile(text_content, int(text_seciton["virtual_address"].replace("0x", ""), 16), capstone_mode)
			return decompiled
		return None

	def decompile_text(self):
		full_source = {

		}
		code_sections = []
		capstone_mode = get_capstone_mode(self.target_architecture, self.is_64_bit)
		for index, key in enumerate(self.sections_with_name.keys()):
			text_seciton = self.sections_with_name[key]
			#if(text_seciton["flags"] == 0x4 and text_seciton["flags"] == 0x1):
			#	pass
			if(text_seciton["type"] == 0x1 and text_seciton["flags"] == 0x6):
				pass
			else:
				continue
			text_content = self.read_with_offset(text_seciton["file_offset"], text_seciton["size"], False)			
			decompiled, registered_touched = decompile(text_content, int(text_seciton["virtual_address"].replace("0x", ""), 16), capstone_mode)
			full_source[index] = [key, decompiled, registered_touched]
			code_sections.append(key)
		self.code_sections = code_sections

		return full_source


	def reconstruct_small(self, section, input_bytes):
	#	print(self.sections_with_name[section])
	#	print(len(input_bytes))
	#	print(len(bytearray(input_bytes)))

		readjust_section = [

		]
		#	[48,8B,05,6D,0B,20,00]

		delta = len(bytearray(input_bytes)) - self.sections_with_name[section]["size"]
#		print(delta)
#		print(bytearray(input_bytes))
#		print()
		for key in self.sections_with_name.keys():
			if(self.sections_with_name[section]["file_offset"] <= self.sections_with_name[key]["file_offset"]):
#				print(self.sections_with_name[key]["file_offset"])
				readjust_section.append(key)
				print("{}	{}	{}".format(self.sections_with_name[key]["file_offset"], self.sections_with_name[key]["size"], self.sections_with_name[key]["file_offset"] + self.sections_with_name[key]["size"]))
		
		x = bytearray(self.sections_with_name[section]["size"])
		print(len(x))
		x[:len(input_bytes)] = input_bytes


		print(delta)

#		assert delta <= 0
#		results = (int_to_bytearray(len(bytearray(input_bytes)), 8))
		results = (int_to_bytearray(len(input_bytes), 8))
		print(results)
		print(self.sections_with_name[section]["orginal_size"])
	#	results.reverse()

		self.write_with_offset(self.sections_with_name[section]["section_location"] + 0x20, results)
		self.write_with_offset(self.sections_with_name[section]["file_offset"], x)
#		print(results)
#		print(self.read_with_offset(self.sections_with_name[section]["section_location"] + 0x20, 8 , reverse=False))
#		print(int_from_bytearray(self.read_with_offset(self.sections_with_name[section]["section_location"] + 0x20, 8 )))#, reverse=True)))	
#		self.file[self.sections_with_name[section]["section_location"] + 8: self.sections_with_name[section]["section_location"] + 16] = results


		open("test_patch", "wb").write(self.file)



	def reconstruct(self, start, end, new_bytes):		
		window_start = self.file[0:start]
		window_end = self.file[end:]
		window = new_bytes

		reconstructed = window_start + window + window_end


	def __init__(self, name):
		self.file = open(name, "rb").read()

		self.is_64_bit = self.file[0x04] == 2
		self.extra_offset = 0 if not self.is_64_bit else 4

		self.section_headers = {

		}

		self.program_headers = {

		}

		target_architecture_lookup = {
			0x00:"No specific instruction set",
			0x02:"SPARC",
			0x03:"x86",
			0x08:"MIPS",
			0x14:"PowerPC",
			0x16:"S390",
			0x28:"ARM",
			0x2A:"SuperH",
			0x32:"IA-64",
			0x3E:"x86-64",
			0xB7:"AArch64",
			0xF3:"RISC-V"
		}

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
		else:
			self.program_entry_point = int_from_bytearray(self.read_with_offset(0x18, 4))

			self.program_header_start = int_from_bytearray(self.read_with_offset(0x1C, 4))
			self.program_header_count = int_from_bytearray(self.read_with_offset(0x2C, 2))
			self.program_header_size = int_from_bytearray(self.read_with_offset(0x2A, 2))

			self.section_headers_start = int_from_bytearray(self.read_with_offset(0x20, 4))
			self.section_headers_size = int_from_bytearray(self.read_with_offset(0x2E, 2))
			self.section_headers_count = int_from_bytearray(self.read_with_offset(0x30, 2))
			self.section_headers_names = int_from_bytearray(self.read_with_offset(0x32, 2))
		

		for i in range(self.section_headers_count):
			self.section_headers[i] = self.parse_section_header(self.section_headers_start + self.section_headers_size * i)
		
		for i in range(self.program_header_count):
			self.program_headers[i] = self.parse_program_header(self.program_header_start + self.program_header_size * i)

		assert self.program_header_start < self.section_headers_start

		self.get_section_names()
		self.decompile_text()
		
if __name__ == "__main__":
	elf(sys.argv[1])


