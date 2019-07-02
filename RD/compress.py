

from collections import OrderedDict
from static.control_flow import *
from static.disassemble import *
import os
import pickle
import json
from elf.elf_parser import *
import zlib  
import binascii


'''
	-	34.392134472587784 compressed <3
		-	decompile_compress will be standard soon.
'''

def test_zlib(data):
	compress = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, +15)  
	compressed_data = compress.compress(data)  
	compressed_data += compress.flush()


	data2 = zlib.decompressobj()  
	decompressed_data = data2.decompress(compressed_data)#[i:i+1024])
	decompressed_data += data2.flush()

	decompressed_data = str(decompressed_data)

	print('Original: %i' % len(data) )
	print('Compressed data: %i' % len(str(binascii.hexlify(compressed_data))))


static = elf("./test_binaries/static_v2")
code_sections = static.get_sections_parsed()

capstone_mode = get_capstone_mode(static.target_architecture, static.is_64_bit)

decompiled_sections = {

}
instructions_value = OrderedDict()
for index, key in code_sections.items():
		print("Targett == {}".format(key))
		text_content, virtual_address = static.read_section(key)
		decompiled, registered_touched, instructions_value = decompile(text_content, virtual_address, capstone_mode, instructions_value)
		decompiled_sections[index] = {
										"section_name":key, 
										"code":decompiled, 
										"registers":registered_touched
									}
import sys

print( sys.getsizeof(decompiled_sections))
print(len(json.dumps(decompiled_sections)))
test_zlib( str(json.dumps(decompiled_sections)).encode())


decompiled_sections = {

}
instructions_value = OrderedDict()
for index, key in code_sections.items():
		print("Targett == {}".format(key))
		text_content, virtual_address = static.read_section(key)
		decompiled, registered_touched, instructions_value = decompile_compress(text_content, virtual_address, capstone_mode, instructions_value)
		decompiled_sections[index] = {
										"section_name":key, 
										"code":decompiled
									}
decompiled_sections["instructions_value"] = list(instructions_value.keys())
#print(instructions_value.keys())

print( sys.getsizeof(decompiled_sections))
print(len(json.dumps(decompiled_sections)))
test_zlib( str(json.dumps(decompiled_sections)).encode())

