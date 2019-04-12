from disassemble import *
import sys
from control_flow_last import *

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
		else:
			section_virtual_address = (hex(int_from_bytearray(self.read_with_offset(start + 0x0C, 4))))
			section_file_offset = int_from_bytearray(self.read_with_offset(start + 0x10, 4))
			section_size = int_from_bytearray(self.read_with_offset(start + 0x14, 4))

		section = {
			"section_location":start,
			"orginal_size":self.read_with_offset(start + 0x20, 8),
			"name_index":section_name,
			"type":int_from_bytearray(section_type),
			"flags":int_from_bytearray(section_flags),
			"virtual_address":section_virtual_address,
			"file_offset":section_file_offset,
			"size":section_size	
		}
		return section

	def parse_program_header(self, start):
		program_header_type = self.read_with_offset(start, 4)


		if(self.is_64_bit):
			program_header_viritual_address = int_from_bytearray(self.read_with_offset(start + 0x10, 8))
		else:
			program_header_viritual_address = int_from_bytearray(self.read_with_offset(start + 0x10, 8))
#		print(hex(program_header_viritual_address))
#		print(hex(int_from_bytearray(program_header_type)))



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
			name = (self.read_zero_terminated_string(string_table_offset + self.section_headers[i]["name_index"]))
#			print(name)
			self.sections_with_name[name] = self.section_headers[i]


	def decompile_section(self, section_name):
		text_seciton = self.sections_with_name[section_name]
		if(text_seciton["type"] == 0x1 and text_seciton["flags"] == 0x6):
			text_content = self.read_with_offset(text_seciton["file_offset"], text_seciton["size"], False)
			results = decompile(text_content, int(text_seciton["virtual_address"].replace("0x", ""), 16), self.is_64_bit)
			return results
		return None

	def decompile_text(self):
		full_source = []
		for i in self.sections_with_name.keys():
			text_seciton = self.sections_with_name[i]
			#if(text_seciton["flags"] == 0x4 and text_seciton["flags"] == 0x1):
			#	pass
			if(text_seciton["type"] == 0x1 and text_seciton["flags"] == 0x6):
				pass
			else:
				continue
			full_source.append([[i]])
			text_content = self.read_with_offset(text_seciton["file_offset"], text_seciton["size"], False)
			
			#if(text_seciton["name"])
			if(i == ".init"):
				print(text_content)

			results = decompile(text_content, int(text_seciton["virtual_address"].replace("0x", ""), 16), self.is_64_bit)
			full_source.extend(results)

		return full_source


	def reconstruct_small(self, section, input_bytes):
		print(self.sections_with_name[section])
		print(len(input_bytes))
		print(len(bytearray(input_bytes)))

		readjust_section = [

		]
		#	[48,8B,05,6D,0B,20,00]

		delta = len(bytearray(input_bytes)) - self.sections_with_name[section]["size"]
		print(delta)
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

		'''
		#for 
		import sys
		some_int = 0

		some_bytes = some_int.to_bytes(32, sys.byteorder)
		my_bytearray = bytearray(some_bytes)
		'''
		print(readjust_section)



	def reconstruct(self, start, end, new_bytes):
		


		window_start = self.file[0:start]
		window_end = self.file[end:]
		window = new_bytes

		reconstructed = window_start + window + window_end


#		print(reconstructed)

	def __init__(self, name):
		self.file = open(name, "rb").read()

		self.is_64_bit = self.file[0x04] == 2
		self.extra_offset = 0 if not self.is_64_bit else 4

		self.section_headers = {

		}

		self.program_headers = {

		}

		if(self.is_64_bit):
			self.program_header_start = int_from_bytearray(self.read_with_offset(0x20, 8))
			self.program_header_count = int_from_bytearray(self.read_with_offset(0x38, 2))
			self.program_header_size = int_from_bytearray(self.read_with_offset(0x36, 2))

			self.section_headers_start = int_from_bytearray(self.read_with_offset(0x28, 8))
			self.section_headers_size = int_from_bytearray(self.read_with_offset(0x3A, 2))
			self.section_headers_count = int_from_bytearray(self.read_with_offset(0x3C, 2))
			self.section_headers_names = int_from_bytearray(self.read_with_offset(0x3E, 2))		
		else:
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


#		print(self.section_headers[2]["orginal_size"])
#		print(self.section_headers[2]["size"])
#		print(list(self.section_headers[2]["orginal_size"]))
#		print(list(int_to_bytearray(32, 8)))

		self.get_section_names()
	
		self.decompile_text()
		

		ret_stop = []
		code = self.decompile_section(".text")
#		code = self.decompile_section(".init")
		for i in range(len(code)):
			ret_stop.append(code[i])
			if("ret" in code[i][1][0]):
				break

		self.control = dowork(ret_stop)
		print(self.control)
	#	print(self.program_header_start)		
	#	print(hex(int_from_bytearray(self.program_header_start)))
	#	self.start_program_header = self.file[0x18: 0x18 + 4 + self.extra_offset]
	#	self.start_program_header = reverse_bytearray(self.start_program_header)
	#	self.start_program_header = int_from_bytearray(self.start_program_header)


if __name__ == "__main__":
	elf(sys.argv[1])


