from capstone import *
from .assembler import *
from collections import OrderedDict

def get_capstone_mode(architecture, is_64, extra=None):
	lookup_architecture_capstone =	{
			"SPARC":CS_ARCH_SPARC,
			"x86":CS_ARCH_X86,
			"MIPS":CS_ARCH_MIPS,
			"PowerPC":CS_ARCH_PPC,
			"ARM":CS_ARCH_ARM,
			"x86-64":CS_ARCH_X86
	}
	if(is_64):
		return Cs(lookup_architecture_capstone[architecture], CS_MODE_64)
	else:
		return Cs(lookup_architecture_capstone[architecture], CS_MODE_32)
	if(extra):
		#	needed for arm etc
		raise Exception("Not implemented")

def get_all_registers(CsInsn):
	registers = []
	index = 1
	while True:
		try:
			registers.append(CsInsn.reg_name(index))
		except Exception:
			break
	return registers

def decompile(input_bytes, start_address, mode, qword):
	decompiled = OrderedDict()
	target_registers_ids = set()
	target_registers_names = []
	mode.detail = True

	next_pointer = None
	next_pointer_address = None

	new_comments = {

	}
	for dissably in mode.disasm(input_bytes, start_address):
		registers = []
		(regs_read, regs_write) = dissably.regs_access()

		if len(regs_read) > 0:
			for r in regs_read:
				registers.append(dissably.reg_name(r))
	
		if len(regs_write) > 0:
			for r in regs_write:
				registers.append(dissably.reg_name(r))

		decompiled["0x%x" % (dissably.address)] = {	
					"instruction":dissably.mnemonic, 
					"argument":dissably.op_str, 
					"registers":list(set(registers)),
					"address_int":dissably.address,
					"comment":""
				}

		if not next_pointer_address == None:			
			if(hex(dissably.address + next_pointer) in qword.keys()):
				if(next_pointer_address in decompiled.keys()):
					decompiled[next_pointer_address]["comment"] = qword[hex(dissably.address + next_pointer)]
			else:
				if(next_pointer_address in decompiled.keys()):
					decompiled[next_pointer_address]["comment"] = hex(dissably.address + next_pointer)
			next_pointer_address = None

		#	can actually be pre calculated by instruction size
		if("rip + " in dissably.op_str and "qword ptr" in dissably.op_str):
			try:
				next_pointer_address = "0x%x" % (dissably.address)
				next_pointer =  int(dissably.op_str[dissably.op_str.index("0x"):-1], 16)
			except Exception as e:
				pass
				
		if("0x%x" % (dissably.address) in qword.keys()):
			decompiled["0x%x" % (dissably.address)]["comment"] = qword["0x%x" % (dissably.address)]
		

	for register_id in target_registers_ids:
		target_registers_names.append(dissably.reg_name(register_id))


	return decompiled, target_registers_names, new_comments



