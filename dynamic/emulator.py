from unicorn import *
from unicorn.x86_const import *
from capstone import *
import struct

from dynamic_linker import *
from elf.elf_parser import *
from .helpful_linker import *
from .unicorn_helper import *
import time
import sys
import os

#test_target = elf("./test_binaries/for_loop_dynamic")
target = elf("./test_binaries/static_v2")

emulator = Uc(UC_ARCH_X86, UC_MODE_64)

'''
	THANKS GDB FOR THE WATCH COMMAND <3

'''



'''
	special instruction 
		cpuid -> https://c9x.me/x86/html/file_module_x86_id_45.html


'''



'''
	Program memory
'''

BASE = 0x400000
program_size =  1024 * 1024 * 8

emulator.mem_map(BASE, program_size)



target_start = None
target_end = None

section_viritual_map = {
	
}

section_map = {
	
}

for name, content in (target.sections_with_name).items():
	section_map[name] = [BASE +  int(content["virtual_address"],16), BASE +  int(content["virtual_address"],16) + content["size"]]
	if(name == ".symtab"):# or name == ".bss"):
		continue

	file_offset = content["file_offset"]
	file_end = file_offset + int(content["size"])
	section_bytes = target.file[file_offset:file_end]

	start = int(content["virtual_address"],16)
	end = int(content["virtual_address"],16) + int(content["size"])
	while emulator.mem_read(BASE + int(content["virtual_address"],16), (file_end-file_offset)) != section_bytes:	
		emulator.mem_write(BASE + int(content["virtual_address"],16), section_bytes)

	if(content["size"] > 0):
		section_viritual_map[name] = [start, end]

'''
	stack memory
'''
stack_adr = 0x1200000
stack_size =  (1024 * 1024 * 8) * 8



#	0x19fffff

print(stack_size)


emulator.mem_map(stack_adr, stack_size)
emulator.reg_write(UC_X86_REG_RSP, stack_adr + stack_size - 1)

'''
	* Dynamic mapping will happen here *
		-	already coded part of the linker
		-	will have a static binary running before more work on dynamic
'''


address_space = {
	"stack":[stack_adr, stack_adr + stack_size],
	"program":[BASE, BASE + program_size]
}



unicorn_debugger = unicorn_debug(emulator, section_viritual_map, section_map, address_space)

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
'''
	xgetbv
		https://www.felixcloutier.com/x86/xgetbv

'''


unicorn_debugger.add_breakpoint(0x800e01, "exit")




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
	if access == UC_MEM_WRITE:
		bold_print(">>> Memory is being WRITE at 0x%x(%s), data size = %u, data value = 0x%x" %(address, unicorn_debugger.determine_location(address) , size, value))
	else:
		bold_print(">>> Memory is being READ at 0x%x (%s), data size = %u" %(address, unicorn_debugger.determine_location(address),  size))
		return True

#	writing fake args 
emulator.mem_write(emulator.reg_read(UC_X86_REG_RSP) - 8, bytes(reversed(bytes(bytearray.fromhex("0x01".replace("0x", ""))))))
emulator.reg_write(UC_X86_REG_RSP, emulator.reg_read(UC_X86_REG_RSP) - 8)

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


