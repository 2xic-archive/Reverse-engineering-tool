
from keystone import *

def get_keystone_mode(architecture, is_64, extra=None):
	lookup_architecture_keystone =	{
			"SPARC":KS_ARCH_SPARC,
			"x86":KS_ARCH_X86,
			"MIPS":KS_ARCH_MIPS,
			"PowerPC":KS_ARCH_PPC,
			"ARM":KS_ARCH_ARM,
			"x86-64":KS_ARCH_X86
	}
	if(is_64):
		return Ks(lookup_architecture_keystone[architecture], Ks_MODE_64)
	else:
		return Ks(lookup_architecture_keystone[architecture], Ks_MODE_32)
	if(extra):
		#	needed for arm etc
		raise Exception("Not implemented")


def assemble(instruction, mode):
	encoding, count = mode.asm(instruction)
	return encoding
