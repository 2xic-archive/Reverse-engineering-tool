from capstone import *
from assembler import *

def diff_decompileiton(input_, start_address):
	mode = Cs(CS_ARCH_X86, CS_MODE_64)
	string = ""
	for dissably in mode.disasm(input_, start_address):
		string += "%s %s;" % (dissably.mnemonic, dissably.op_str)
	return string

def decompile(input_bytes, start_address, is_64=True, check=True):
	mode = None 
	results = []
	if(is_64):
		mode = Cs(CS_ARCH_X86, CS_MODE_64)
	else:
		mode = Cs(CS_MODE_ARM, CS_MODE_ARM)

	string = ""
	results_stirng = []
	for dissably in mode.disasm(input_bytes, start_address):
		#print("0x%x:\t%s\t[%s]" % (dissably.address, dissably.mnemonic, dissably.op_str))
		
		if(dissably.mnemonic == "ret"):
			print("")
		'''
		if("rip +" in dissably.op_str):
			truth = decode_control_flow(dissably.op_str , dissably.address + 1)
			op_str = dissably.op_str.split("ptr")[0] + "[{}]".format(hex(truth))
			#print("")
		#	print("0x%x:\t%s\t%s" % (dissably.address, dissably.mnemonic, dissably.op_str))
			results.append([["0x%x" % (dissably.address)], ["%s\t%s" % (dissably.mnemonic, op_str)]])
			#print("")
		else:
		'''
	#	if("jmp" in dissably.mnemonic and "qword" not in dissably.op_str):
#			print(dissably.mnemonic)
#			print(int(dissably.op_str, 16))
#			print(int(dissably.op_str, 16) - start_address)
#			exit(0)
		#	string += "%s %s;" % (dissably.mnemonic, (int(dissably.op_str, 16) - start_address))
		#	results.append([["0x%x" % (dissably.address)], ["%s\t%s" % (dissably.mnemonic, (int(dissably.op_str, 16) - start_address))]])
		#else:
		#	string += "%s %s;" % (dissably.mnemonic, dissably.op_str)
		results.append([["0x%x" % (dissably.address)], ["%s\t%s" % (dissably.mnemonic, dissably.op_str)]])
		string += "%s %s;" % (dissably.mnemonic, dissably.op_str)

	#assert diff_decompileiton(bytes(assemble(string)), start_address) 

	return results


