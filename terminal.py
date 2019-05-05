from elf.elf_parser import *
from static.assembler import *
from model import *
from elf.elf_parser_key_value import *



#from dynamic.parsing_libc import *
#exit(0)

from dynamic.dynamic_linker import *
from dynamic.emulator import *


#target = model(elf(sys.argv[1]))



#print(target)



#print(target.static.read_section_bytes(".data"))



#target.decompile_binary()


'''
overlap = []

overlap_program = {
	
}


for index, key in (target.static.program_headers).items():
#	overlap.append(key["file_offset"])# + key["file_size"])

	if(key["file_size"] > 0):
		overlap.append(key["file_offset"])
		overlap_program[key["file_offset"]] = key["type_name"]
		print(hex(key["virtual_address"]))
#	print("{} {}".format(key["file_offset"], key["type_name"]))


overlap_section = {
	
}
for index, key in (target.static.sections_with_name).items():
#	if(key["file_offset"] == 0):
	if(key["size"] > 0):
		overlap_section[key["file_offset"]] = index #target.static.get_section_name_by_index(key["name_index"])

keystotal = list(overlap_section.keys())
keystotal.extend(list(overlap_program.keys()))

for j in sorted(keystotal):
	print("{}	{}".format(overlap_program.get(j, "huff"), overlap_section.get(j, "huff")))

#print(target.static.sections_with_name)
print(sorted(keystotal))
'''


	# + key["file_size"])



#print(target.)

'''
get_dynamic_symbols(target.static)



for key, typed in target.static.sections_with_name.items():
	if(typed["type"] == 0x0B):
		print(key)
exit(0)


'''
'''		
print(target.static.sections_with_name[".rela.dyn"])


for section in [".rela.dyn", ".rela.plt"]:
	parse_relocation(target.static, section)

'''