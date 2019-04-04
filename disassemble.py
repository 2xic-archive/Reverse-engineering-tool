from capstone import *

def decompile(inpu_bytes, start_address, is_64=True):
	mode = None 
	if(is_64):
		mode = Cs(CS_ARCH_X86, CS_MODE_64)
	else:
		mode = Cs(CS_MODE_ARM, CS_MODE_ARM)

	for dissably in mode.disasm(inpu_bytes, start_address):
		print("0x%x:\t%s\t%s" % (dissably.address, dissably.mnemonic, dissably.op_str))
		if(dissably.mnemonic == "ret"):
			print("")
