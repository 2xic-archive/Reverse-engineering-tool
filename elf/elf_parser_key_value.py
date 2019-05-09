
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

def get_readable_flags(flag_value):
	flag_id = [
		[0x1, "SHF_WRITE"],
		[0x2, "SHF_ALLOC"],
		[0x4, "SHF_EXECINSTR"],
		[0x10, "SHF_MERGE"],
		[0x20, "SHF_STRINGS"],
		[0x40, "SHF_INFO_LINK"],
		[0x80, "SHF_LINK_ORDER"],
		[0x100, "SHF_OS_NONCONFORMING"],
		[0x200, "SHF_GROUP"],
		[0x400, "SHF_TLS"],
		[0x0ff00000, "SHF_MASKOS"],
		[0xf0000000, "SHF_MASKPROC"],
		[0x4000000, "SHF_ORDERED"],
		[0x8000000, "SHF_EXCLUDE"]
	]
	flags = []
	for flag_id in flag_id:
		if(flag_value & flag_id[0]):
			flags.append(flag_id[1])
		if(flag_value < flag_id[0]):
			break
	return flags

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

#	thanks https://github.com/detailyang/readelf/blob/master/readelf/readelf.py
TAG = {
	0:"NULL",
	1:"NEEDED",
	2:"PLTRELSZ",
	3:"PLTGOT",
	4:"HASH",
	5:"STRTAB",
	6:"SYMTAB",
	7:"RELA",
	8:"RELASZ",
	9:"RELAENT",
	10:"STRSZ",
	11:"SYMENT",
	12:"INIT",
	13:"FINI",
	14:"SONAME",
	15:"RPATH",
	16:"SYMBOLIC",
	17:"REL",
	18:"RELSZ",
	19:"RELENT",
	20:"PLTREL",
	21:"DEBUG",
	22:"TEXTREL",
	23:"JMPREL",
	24:"BIND_NOW",
	25:"INIT_ARRAY",
	26:"FINI_ARRAY",
	27:"INIT_ARRAYSZ",
	28:"FINI_ARRAYSZ",
	29:"RUNPATH",
	30:"FLAGS",
	32:"ENCODING",
	32:"PREINIT_ARRAY",
	33:"PREINIT_ARRAYSZ",
	34:"MAXPOSTAGS",
	0x6000000d:"LOOS",
	0x6000000d:"SUNW_AUXILIARY",
	0x6000000e:"SUNW_RTLDINF",
	0x6000000e:"SUNW_FILTER",
	0x60000010:"SUNW_CAP",
	0x60000011:"SUNW_SYMTAB",
	0x60000012:"SUNW_SYMSZ",
	0x60000013:"SUNW_ENCODING",
	0x60000013:"SUNW_SORTENT",
	0x60000014:"SUNW_SYMSORT",
	0x60000015:"SUNW_SYMSORTSZ",
	0x60000016:"SUNW_TLSSORT",
	0x60000017:"SUNW_TLSSORTSZ",
	0x60000018:"SUNW_CAPINFO",
	0x60000019:"SUNW_STRPAD",
	0x6000001a:"SUNW_CAPCHAIN",
	0x6000001b:"SUNW_LDMACH",
	0x6000001d:"SUNW_CAPCHAINENT",
	0x6000001f:"SUNW_CAPCHAINSZ",
	0x6ffff000:"HIOS",
	0x6ffffd00:"VALRNGLO",
	0x6ffffdf8:"CHECKSUM",
	0x6ffffdf9:"PLTPADSZ",
	0x6ffffdfa:"MOVEENT",
	0x6ffffdfb:"MOVESZ",
	0x6ffffdfd:"POSFLAG_1",
	0x6ffffdfe:"SYMINSZ",
	0x6ffffdff:"SYMINENT",
	0x6ffffdff:"VALRNGHI",
	0x6ffffe00:"ADDRRNGLO",
	0x6ffffefa:"CONFIG",
	0x6ffffefb:"DEPAUDIT",
	0x6ffffefc:"AUDIT",
	0x6ffffefd:"PLTPAD",
	0x6ffffefe:"MOVETAB",
	0x6ffffeff:"SYMINFO",
	0x6ffffeff:"ADDRRNGHI",
	0x6ffffff9:"RELACOUNT",
	0x6ffffffa:"RELCOUNT",
	0x6ffffffb:"FLAGS_1",
	0x6ffffffc:"VERDEF",
	0x6ffffffd:"VERDEFNUM",
	0x6ffffffe:"VERNEED",
	0x6fffffff:"VERNEEDNUM",
	0x70000000:"LOPROC",
	0x70000001:"SPARC_REGISTER",
	0x7ffffffd:"AUXILIARY",
	0x7ffffffe:"USED",
	0x7fffffff:"FILTER",
	0x7fffffff:"HIPROC",
	}




STT_TYPE = {
	0: "NOTYPE",
	1: "OBJECT",
	2: "FUNC",
	3: "SECTION",
	4: "FILE",
	5: "COMMON",
	6: "TLS",
	10: "LOOS",
	12: "HIOS",
	13: "LOPROC",
	15: "HIPROC"
}


STB_BIND = {
	0: "LOCAL",
	1: "GLOBAL",
	2: "WEAK",
	13: "LOPROC",
	15: "HIPROC"
}


STV_VISIBILITY = {
	0: "DEFAULT",
	1: "INTERNAL",
	2: "HIDDEN",
	3: "PROTECTED"
}

SH_TYPE = {
	0:"NULL",
	1:"PROGBITS",
	2:"SYMTAB",
	3:"STRTAB",
	4:"RELA",
	5:"HASH",
	6:"DYNAMIC",
	7:"NOTE",
	8:"NOBITS",
	9:"REL",
	10:"SHLIB",
	11:"DYNSYM",
	14:"INIT_ARRAY",
	15:"FINI_ARRAY",
	16:"PREINIT_ARRAY",
	17:"GROUP",
	18:"SYMTAB_SHNDX",
	0x60000000:"LOOS",
	0x6fffffff:"HIOS",
	0x70000000:"LOPROC",
	0x7fffffff:"HIPROC",
	0x80000000:"LOUSER",
	0xffffffff:"HIUSER",
}


def ELF_ST_TYPE(i):
	return ((i)&0x0f)

def ELF_ST_VISIBILITY(i):
	return ((i)&0x3)

def ELF_ST_BIND(i):
	return ((i) >> 4)

def ELF64_R_SYM(i):
	return i >> 32

def ELF32_R_SYM(i):
	return i >> 8



