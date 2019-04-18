from elf_parser_key_value import *
import struct


'''
	-	need to be able to know what symbols and what libraries
		are needed to be loaded into unicorn.
'''
def get_dynamic_symbols(elf_target):
	dynamic_section_str_start = elf_target.sections_with_name[".dynstr"]["file_offset"]

	dynamic_section_sym_start = elf_target.sections_with_name[".dynsym"]["file_offset"]
	dynamic_section_sym_entry_size = elf_target.sections_with_name[".dynsym"]["entries_size"]
	dynamic_section_sym_end = elf_target.sections_with_name[".dynsym"]["file_offset"] + elf_target.sections_with_name[".dynsym"]["size"]

	index = 0
	for offset in range(dynamic_section_sym_start, dynamic_section_sym_end, dynamic_section_sym_entry_size):
		struct_format = "IBBHQQ" if(elf_target.is_64_bit) else "IIIBBH"

		st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack(struct_format, elf_target.file[offset:offset+dynamic_section_sym_entry_size])

		st_name = elf_target.read_zero_terminated_string(dynamic_section_str_start + st_name)
		print("%04d%10d%10d%10s%10s%10s%10d\t%s" %(index, st_value, st_size, STT_TYPE[ELF_ST_TYPE(st_info)],
					STB_BIND[ELF_ST_BIND(st_info)], STV_VISIBILITY[ELF_ST_VISIBILITY(st_other)], st_shndx, st_name))
		index += 1

def parse_dynamic(elf_target):
	dynamic_section_str_start = elf_target.sections_with_name[".dynstr"]["file_offset"]

	dynamic_section_start = elf_target.sections_with_name[".dynamic"]["file_offset"]
	dynamic_section_size_entry = (elf_target.sections_with_name[".dynamic"]["entries_size"])
	dynamic_section_end = dynamic_section_start + elf_target.sections_with_name[".dynamic"]["size"]

	for offset in range(dynamic_section_start, dynamic_section_end, dynamic_section_size_entry):
		tag, identity = struct.unpack('QQ', (elf_target.file[offset:offset+dynamic_section_size_entry]))
		if tag in TAG:
			if tag == 1 or tag == 15:
				print('0x%018x %20s [%s]' %(tag, TAG[tag], elf_target.read_zero_terminated_string(dynamic_section_str_start + identity)))
			else:
				print('0x%018x %20s [0x%x]' %(tag, TAG[tag], identity))
		else:
			print('0x%018x %20s [0x%x]' %(tag, tag, identity))


def get_got(elf_target):
	get_dynamic_symbols(elf_target)
	parse_dynamic(elf_target)
	exit(0)
