
from elf.elf_parser_key_value import *
import struct


'''
	-	need to be able to know what symbols and what libraries
		are needed to be loaded into unicorn.
	-	not sure if this should be in the elf parser or not...
'''

#	good manpage http://manpages.courier-mta.org/htmlman5/elf.5.html

def get_dynamic_symbols(elf_target, name, debug=False):
#	global symbol_table


	dynamic_section_str_start = elf_target.sections_with_name[".dynstr"]["file_offset"]

	dynamic_section_sym_start = elf_target.sections_with_name[name]["file_offset"]
	dynamic_section_sym_entry_size = elf_target.sections_with_name[name]["entries_size"]
	dynamic_section_sym_end = elf_target.sections_with_name[name]["file_offset"] + elf_target.sections_with_name[name]["size"]


	index = 0
	lookup_table = {

	}
	for offset in range(dynamic_section_sym_start, dynamic_section_sym_end, dynamic_section_sym_entry_size):
		struct_format = "IBBHQQ" if(elf_target.is_64_bit) else "IIIBBH"

		st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack(struct_format, elf_target.file[offset:offset+dynamic_section_sym_entry_size])

		st_name = elf_target.read_zero_terminated_string(dynamic_section_str_start + st_name)

		if(debug):
			print("%x\t%04d%10d%10d%10s%10s%10s%10d\t%s" % (offset, index, st_value, st_size, STT_TYPE[ELF_ST_TYPE(st_info)],
						STB_BIND[ELF_ST_BIND(st_info)], STV_VISIBILITY[ELF_ST_VISIBILITY(st_other)], st_shndx, st_name))

		if(len(st_name) > 0):
			lookup_table[st_name] = hex(st_value)


		elf_target.symbol_table[index] = st_name
		index += 1

	return lookup_table


def parse_relocation(elf_target, target, debug=False):
	
	dynamic_section_sym_start = elf_target.sections_with_name[target]["file_offset"]
	dynamic_section_sym_entry_size = elf_target.sections_with_name[target]["entries_size"]
	dynamic_section_sym_end = elf_target.sections_with_name[target]["file_offset"] + elf_target.sections_with_name[target]["size"]

	index = 0

#	print("offset 	symbol 	type")
	lookup = {

	}

	for offset in range(dynamic_section_sym_start, dynamic_section_sym_end, dynamic_section_sym_entry_size):
		if(elf_target.is_64_bit):
			struct_format = "QQQ"
			address,info,addend = struct.unpack(struct_format, elf_target.file[offset:offset+dynamic_section_sym_entry_size])
			try:
				elf_target.qword_helper[hex(address)] = elf_target.symbol_table[ELF64_R_SYM(info)]
				if(debug):
					print((hex(address), info, addend), elf_target.symbol_table[ELF64_R_SYM(info)])
					if(len(elf_target.symbol_table[ELF64_R_SYM(info)]) > 0):
						lookup[elf_target.symbol_table[ELF64_R_SYM(info)]] = address
			except Exception as e:
				print("erorr in parse_relocation")
	return lookup


def parse_dynamic(elf_target):
	dynamic_section_str_start = elf_target.sections_with_name[".dynstr"]["file_offset"]

	dynamic_section_start = elf_target.sections_with_name[".dynamic"]["file_offset"]
	dynamic_section_size_entry = (elf_target.sections_with_name[".dynamic"]["entries_size"])
	dynamic_section_end = dynamic_section_start + elf_target.sections_with_name[".dynamic"]["size"]

	for offset in range(dynamic_section_start, dynamic_section_end, dynamic_section_size_entry):
		tag, identity = struct.unpack("QQ", (elf_target.file[offset:offset+dynamic_section_size_entry]))
		if tag in TAG:
			if tag == 1 or tag == 15:
				print("0x%018x %20s [%s]" %(tag, TAG[tag], elf_target.read_zero_terminated_string(dynamic_section_str_start + identity)))
			else:
				print("0x%018x %20s [0x%x]" %(tag, TAG[tag], identity))
		else:
			print("0x%018x %20s [0x%x]" %(tag, tag, identity))
