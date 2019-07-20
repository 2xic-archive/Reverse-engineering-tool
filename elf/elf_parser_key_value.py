
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

'''
	Thank you
	http://openpowerfoundation.org/wp-content/uploads/resources/leabi/content/dbdoclet.50655241_51269.html
	https://www.intezer.com/executable-and-linkable-format-101-part-3-relocations/
	https://github.com/serpilliere/elfesteem/blob/master/elfesteem/elf.py
'''
ELF_RELA_TYPE = {
	"A": "Addend of Elfxx_Rela entries.",
	"B": "Image base where the shared object was loaded in process virtual address space.",
	"G": "Offset to the GOT relative to the address of the correspondent relocation entry’s symbol.",
	"L": "Section offset or address of the procedure linkage table (PLT, .got.plt).",
	"P": "The section offset or address of the storage unit being relocated. retrieved via r_offset relocation entry’s field.",
	"S": "Relocation entry’s correspondent symbol value.",
	"Z": "Size of Relocations entry’s symbol."
}

ELF_RELA_TYPE_ = ["Addend of Elfxx_Rela entries.",
	"Image base where the shared object was loaded in process virtual address space.",
	"Offset to the GOT relative to the address of the correspondent relocation entry’s symbol.",
	"Section offset or address of the procedure linkage table (PLT, .got.plt).",
	"The section offset or address of the storage unit being relocated. retrieved via r_offset relocation entry’s field.",
	"Relocation entry’s correspondent symbol value.",
	"Size of Relocations entry’s symbol."]

ELF_RELA_TYPE_REAL = {
	0  : "R_X86_64_NONE       - No reloc",
	1  : "R_X86_64_64         - Direct 64 bit", 
	2  : "R_X86_64_PC32       - PC relative 32 bit signed",
	3  : "R_X86_64_GOT32      - 32 bit GOT entry",
	4  : "R_X86_64_PLT32      - 32 bit PLT address",
	5  : "R_X86_64_COPY       - Copy symbol at runtime",
	6  : "R_X86_64_GLOB_DAT   - Create GOT entry",
	7  : "R_X86_64_JUMP_SLOT  - Create PLT entry",
	8  : "R_X86_64_RELATIVE   - Adjust by program base",
	9  : "R_X86_64_GOTPCREL   - 32 bit signed PC relative offset to GOT",
	10 : "R_X86_64_32         - Direct 32 bit zero extended",
	11 : "R_X86_64_32S        - Direct 32 bit sign extended",
	12 : "R_X86_64_16         - Direct 16 bit zero extended",
	13 : "R_X86_64_PC16       - 16 bit sign extended pc relative",
	14 : "R_X86_64_8          - Direct 8 bit sign extended ",
	15 : "R_X86_64_PC8        - 8 bit sign extended pc relative",
	16 : "R_X86_64_DTPMOD64   - ID of module containing symbol",
	17 : "R_X86_64_DTPOFF64   - Offset in module's TLS block",
	18 : "R_X86_64_TPOFF64    - Offset in initial TLS block",
	19 : "R_X86_64_TLSGD      - 32 bit signed PC relative offset to two GOT entries for GD symbol",
	20 : "R_X86_64_TLSLD      - 32 bit signed PC relative offset to two GOT entries for LD symbol",
	21 : "R_X86_64_DTPOFF32   - Offset in TLS block",
	22 : "R_X86_64_GOTTPOFF   - 32 bit signed PC relative offset to GOT entry for IE symbol",
	23 : "R_X86_64_TPOFF32    - Offset in initial TLS block",
	24 : "R_X86_64_PC64       - PC relative 64 bit",
	25 : "R_X86_64_GOTOFF64   - 64 bit offset to GOT",
	26 : "R_X86_64_GOTPC32    - 32 bit signed pc relative offset to GOT",
	27 : "R_X86_64_GOT64      - 64-bit GOT entry offset",
	28 : "R_X86_64_GOTPCREL64 - 64-bit PC relative offset to GOT entry",
	29 : "R_X86_64_GOTPC64    - 64-bit PC relative offset to GOT",
	30 : "R_X86_64_GOTPLT64   - like GOT64, says PLT entry needed",
	31 : "R_X86_64_PLTOFF64   - 64-bit GOT relative offset to PLT entry",
	32 : "R_X86_64_SIZE32     - Size of symbol plus 32-bit addend",
	33 : "R_X86_64_SIZE64     - Size of symbol plus 64-bit addend",
	34 : "R_X86_64_GOTPC32_TLSDESC - GOT offset for TLS descriptor. ",
	35 : "R_X86_64_TLSDESC_CAL- Marker for call through TLS descriptor. ",
	36 : "R_X86_64_TLSDESC    - TLS descriptor. ",
	37 : "R_X86_64_IRELATIVE  - Adjust indirectly by program base",
	38 : "R_X86_64_NUM            "
}

def handle_rela(x):
	return ELF_RELA_TYPE_REAL[x].split(" ")[0]


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

def ELF32_R_TYPE(i):
	return ((i) & 0xff)

def ELF64_R_TYPE(i):
	return ((i) & 0xffffffff)

