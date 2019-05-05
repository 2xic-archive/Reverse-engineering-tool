
from .dynamic_linker import *



def link_lib_and_binary(binary, library):
	binary_map_functions = {

	}
	for section_key, section_info in binary.sections_with_name.items():
		if(section_info["type"] == 0x4):
			for key, item in parse_relocation(binary, section_key, True).items():
				binary_map_functions[key] = item

	print(binary_map_functions)

	look_up_libary_function = {

	}

	for section_key, section_info in library.sections_with_name.items():
		if(section_info["type"] == 0x0B):
			for key, item in get_dynamic_symbols(library, section_key).items():
				look_up_libary_function[key] = item
#	print(look_up_libary_function["__libc_start_main"])
#	print(hex(binary_map_functions["__libc_start_main"]))


	mappings = []
	for key, item in binary_map_functions.items():
		if(look_up_libary_function.get(key, None) != None):
			mappings.append([hex(item), look_up_libary_function[key]])
#	print(mappings)
#	exit(0)
	return mappings
	'''
		kinda working 
	'''