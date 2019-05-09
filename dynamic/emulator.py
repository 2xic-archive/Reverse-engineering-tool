from unicorn import *
from unicorn.x86_const import *
from capstone import *
import struct

from .dynamic_linker import *
from elf.elf_parser import *
from .helpful_linker import *
from .unicorn_helper import *
import time
import sys
import os

target = elf("./test_binaries/static_v2")
emulator = Uc(UC_ARCH_X86, UC_MODE_64)

'''
	special instruction 
		cpuid -> https://c9x.me/x86/html/file_module_x86_id_45.html
	xgetbv
		https://www.felixcloutier.com/x86/xgetbv



	# https://wiki.cdot.senecacollege.ca/wiki/X86_64_Register_and_Instruction_Quick_Start
		nice table
'''


'''
	ideas to resolve problems
		-	check memory layout
			-	 info proc mappings
		-	check if the stack is mapped at end when gdb starts


		rsp : 0x7fffffffec20
		max-rsp : 0x7ffffffff000
		992 seems to be reserved.... intresting...
'''



'''
	Program memory
'''

BASE = 0x400000
program_size =  1024 * 1024 * 8

emulator.mem_map(BASE, program_size)



target_start = None
target_end = None

section_virtual_map = {
	
}

section_map = {
	
}

for name, content in (target.sections_with_name).items():
	section_map[name] = [BASE +  int(content["virtual_address"],16), BASE +  int(content["virtual_address"],16) + content["size"]]

	if(content["type_name"] == "SHT_NOBITS" or not "SHF_ALLOC" in content["flags"]):
		print("Skipped section %s" % (name))
		continue

	file_offset = content["file_offset"]
	file_end = file_offset + int(content["size"])
	section_bytes = target.file[file_offset:file_end]

	start = int(content["virtual_address"],16)
	end = int(content["virtual_address"],16) + int(content["size"])
	emulator.mem_write(BASE + int(content["virtual_address"],16), section_bytes)

	if(content["size"] > 0):
		section_virtual_map[name] = [start, end]


'''
	stack memory
'''
stack_adr = 0x1200000
stack_size =  (1024 * 1024 * 8) # 8 mb stack


emulator.mem_map(stack_adr, stack_size)
emulator.reg_write(UC_X86_REG_RSP, stack_adr + stack_size - 1)


#emulator.mem_map(0x1a00000, 1024 * 1024)


'''
	* Dynamic mapping will happen here *
		-	already coded part of the linker
		-	will have a static binary running before more work on dynamic
'''

address_space = {
	"stack":[stack_adr, stack_adr + stack_size],
	"program":[BASE, BASE + program_size]
}



unicorn_debugger = unicorn_debug(emulator, section_virtual_map, section_map, address_space)

unicorn_debugger.full_trace = True


unicorn_debugger.add_hook("cpuid", {
	0:{
		"RAX":0xd,
		"RBX":0x756e6547,
		"RCX":0x6c65746e,
		"RDX":0x49656e69
	},
	1:{
		"RAX":0x306c1,
		"RBX":0x800,
		"RCX":0xfffa3203,
		"RDX":0x78bfbff
	},
	2:{
		"RAX":0x0,
		"RBX":0x7a9,
		"RCX":0x0,
		"RDX":0x4000000
	},
	3:{
		"RAX":0x7,
		"RBX":0x340,
		"RCX":0x340,
		"RDX":0x0
	},
	4:{
		"RAX":0x1,
		"RBX":0x0,
		"RCX":0x0,
		"RDX":0x0
	}
},
	{
		"max_hit_count":4
	}
)

#	will actually hook xgetbv (since ecx will be zero and trying to hook on xgetbv will be to late....)
unicorn_debugger.add_hook("0x800e01", {
	0:{
		"RAX":0x7,
		"RCX":0x0,
		"RDX":0x0,
		"RIP":0x400e06 + BASE
	}
},
	{
		"max_hit_count":0
	}
)

unicorn_debugger.add_hook("0x834db0", {
	0:{
		"RAX":0x21,
		"RIP":0x434db3 + BASE
	}
},
	{
		"max_hit_count":0
	}
)



'''
	just hardcoded
'''
'''
unicorn_debugger.add_hook("0x834e8a", {
	0:{
		"RIP":0x434e98 + BASE
	}
},
	{
		"max_hit_count":0
	}
)

unicorn_debugger.add_hook("0x834ebf", {
	0:{
		"RIP":0x4350dd + BASE
	}
},
	{
		"max_hit_count":0
	}
)

unicorn_debugger.add_hook("0x834ec8", {
	0:{
		"RIP":0x434eca + BASE
	}
},
	{
		"max_hit_count":0
	}
)

unicorn_debugger.add_hook("0x834ed4", {
	0:{
		"RIP":0x434ed6 + BASE
	}
},
	{
		"max_hit_count":0
	}
)


unicorn_debugger.add_hook("0x834ee0", {
	0:{
		"RIP":0x434ee2 + BASE
	}
},
	{
		"max_hit_count":0
	}
)
'''


#unicorn_debugger.add_breakpoint(0x834e88)
#unicorn_debugger.add_breakpoint(0x834dba)


unicorn_debugger.add_breakpoint(0x800e01, "exit")
#unicorn_debugger.trace_registers("RDI", pause=True)

#unicorn_debugger.add_hook_memory(0x19ffed8, write_only=True)
#unicorn_debugger.add_hook_memory(0x19ffecc, write_only=True)
#unicorn_debugger.add_hook_memory(0x19ffed0, write_only=True) # seems to be this bad boy that makes evreything go out of bounds
#unicorn_debugger.trace_registers("RDX", pause=True)

#unicorn_debugger.add_value_search(0x19fffff)

'''
	happens at the start of the program...
	rdx stores the rsp....
	mov rdx, r13 ?
'''
#	0x19fffff




# callback for tracing basic blocks
def hook_block(uc, address, size, user_data):
    bold_print(">>> Tracing call block at 0x%x(%s), block size = 0x%x" % (address, unicorn_debugger.determine_location(address)  , size))
    print(uc.reg_read(UC_X86_REG_RBP))

def hook_mem_invalid(uc, access, address, size, value, user_data):
	bold_print(">>> Address hit {}({}), size {}".format(hex(address), unicorn_debugger.determine_location(address), size))

def hook_code(mu, address, size, user_data):  
	global unicorn_debugger
	try:
		print('>>> (%x) Tracing instruction at 0x%x  [0x%x] (%s), instruction size = 0x%x' % (unicorn_debugger.instruction_count, address, address-BASE, unicorn_debugger.determine_location(address), size))
		unicorn_debugger.tick(address, size)
	except  Exception as e:
		bold_print("exception stop ....")
		print(e)
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)

		exit(0)

def hook_mem_access(uc, access, address, size, value, user_data):
	global unicorn_debugger
	if access == UC_MEM_WRITE:
		bold_print(">>> Memory is being WRITE at 0x%x(%s), data size = %u, data value = 0x%x" %(address, unicorn_debugger.determine_location(address) , size, value))
	else:
		if(size > 32):
			bold_print(">>> Memory is being READ at 0x%x (%s), data size = %u" %(address, unicorn_debugger.determine_location(address),  size))
		else:
			bold_print(">>> Memory is being READ at 0x%x (%s), data size = %u , data value = %s" %(address, unicorn_debugger.determine_location(address),  size , pretty_print_bytes(uc.mem_read(address, size))))	
	unicorn_debugger.memory_hook_check(address, access == UC_MEM_WRITE)
	unicorn_debugger.check_memory_value(value)

#	writing fake args 
stack_space = 992 # Is this static?
emulator.mem_write(emulator.reg_read(UC_X86_REG_RSP) - stack_space, bytes(reversed(bytes(bytearray.fromhex("0x01".replace("0x", ""))))))
emulator.reg_write(UC_X86_REG_RSP, emulator.reg_read(UC_X86_REG_RSP) - stack_space)


emulator.reg_write(UC_X86_REG_EFLAGS, 0x202)


emulator.hook_add(UC_ERR_WRITE_UNMAPPED, hook_mem_invalid)
emulator.hook_add(UC_HOOK_MEM_INVALID, hook_mem_invalid)


emulator.hook_add(UC_HOOK_MEM_WRITE, hook_mem_access)
emulator.hook_add(UC_HOOK_MEM_READ, hook_mem_access)

emulator.hook_add(UC_MEM_READ_UNMAPPED, hook_mem_invalid)
emulator.hook_add(UC_ERR_READ_UNMAPPED, hook_mem_invalid)
emulator.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED, hook_mem_invalid)

emulator.hook_add(UC_HOOK_BLOCK, hook_block)
emulator.hook_add(UC_HOOK_CODE, hook_code)

unicorn_debugger.setup()
emulator.emu_start(BASE + target.program_entry_point, BASE + target.program_entry_point + 0x50)


