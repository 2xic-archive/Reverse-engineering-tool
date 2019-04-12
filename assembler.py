
from keystone import *


def assemble(instruction, is_64=True):
	mode = None 
	results = []
	if(is_64):
		mode = Ks(KS_ARCH_X86, KS_MODE_64)
	else:
		mode = Ks(KS_MODE_ARM, KS_MODE_ARM)
		raise Exception("not prepra")

	encoding, count = mode.asm(instruction)
	return encoding
