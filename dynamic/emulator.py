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
	if(name == ".symtab" or name == ".bss"):
		continue

	file_offset = content["file_offset"]
	file_end = file_offset + int(content["size"])
	section_bytes = target.file[file_offset:file_end]

	start = int(content["virtual_address"],16)
	end = int(content["virtual_address"],16) + int(content["size"])
	while emulator.mem_read(BASE + int(content["virtual_address"],16), (file_end-file_offset)) != section_bytes:	
		emulator.mem_write(BASE + int(content["virtual_address"],16), section_bytes)

	if(content["size"] > 0):
		#check_section_map(start, end, name)
		section_viritual_map[name] = [start, end]
#	print(section_viritual_map)
#	exit(0)


'''
	stack memory

'''
stack_adr = 0
stack_size =  1024 * 1024

emulator.mem_map(stack_adr, stack_size)
emulator.reg_write(UC_X86_REG_RSP, stack_adr + stack_size - 1)


'''
	tramponline space
'''
tramponline_space = 0x600000
tramponline_size = 1024 * 1024
#	emulator.mem_map(0x600000, tramponline_size)


libc_start = 0x1200000
libc_size = 1024 * 8192 

start_libc_c_program = 0x800000 + 0x201f0
start_frame_dummy = 0x400000 + 0x630
malloc_libc = 0x800000 + 0x7af10
libc_exit = (0x800000 + 0x35980)
frame_dummy_init_array_entry = 0x4006c9
frame_dummy = BASE + 0x630

'''
emulator.mem_map(libc_start, libc_size )


emulator.mem_write(0xb98e40, bytes(reversed(bytes(bytearray.fromhex(hex(malloc_libc).replace("0x", ""))))))
emulator.mem_write(0xb958d8, bytes(reversed(bytes(bytearray.fromhex(hex(libc_exit).replace("0x", ""))))))
emulator.mem_write(0x800000 + 0x5704 + 0x1995d8,  bytes(reversed(bytes(bytearray.fromhex("0xdeadbeef".replace("0x", ""))))))

#	trampoline
emulator.mem_write(0x600fd8, bytes(reversed(bytes(bytearray.fromhex(hex(start_libc_c_program).replace("0x", ""))))))
emulator.mem_write(0x600e08, bytes(reversed(bytes(bytearray.fromhex(hex(start_frame_dummy).replace("0x", ""))))))
'''



'''

	you know what makes me sad? glibc dosen't have all I need. I actually have to load a static binary to get to some functions
	like _dl_fini. GRR!

		-	how should I fix this when we are removing evreything that is hardcoded? 

'''


#static_helper_start = 0x1500000
#emulator.mem_map(static_helper_start, libc_size )
#emulator.mem_write(static_helper_start, open("./test_binaries/static_helper", "rb").read())

#print(emulator.mem_read(libc_start + 12168224, 8))
#xit(0)

'''
	reading libc
'''

#libc_target = elf("/lib/x86_64-linux-gnu/libc.so.6")

'''
for links in link_lib_and_binary(target, libc_target):
	#print(links[1])
	#print(links[1].replace("0x", "").strip())
	#print(bytearray.fromhex(links[1].replace("0x", "").strip()))
	if(len(links[1][2:]) % 2 == 1):
		links[1] = "0" + links[1]
'''
#		print("HM?")
#	print(len(links[1][2:]) % 2)
#	print("")

#	emulator.mem_write(BASE + int(links[0],16), bytes(reversed(bytes(bytearray.fromhex(links[1].replace("0x", ""))))))


#exit(0)

'''
	the memory layout is not linear!

'''

'''
target_start = None
target_end = None
for name, content in (libc_target.sections_with_name).items():
	if(name == ".bss"):
		continue
	file_offset = content["file_offset"]
	file_end = file_offset + int(content["size"])
	emulator.mem_write(libc_start + int(content["virtual_address"],16), libc_target.file[file_offset:file_end])

'''

import time
time.sleep(1)



address_space = {
	"stack":[stack_adr, stack_adr + stack_size],
	"program":[BASE, BASE + program_size]
#	,
#	"random trampoline_sapce":[tramponline_space, tramponline_space + tramponline_size],
#	"libc":[libc_start, libc_start + libc_size]
}



unicorn_debugger = unicorn_debug(emulator, section_viritual_map, section_map, address_space)

unicorn_debugger.full_trace = False


#	unicorn_debugger.add_breakpoint(0x800fe9)
#	unicorn_debugger.add_breakpoint(0x800992)
#	unicorn_debugger.add_breakpoint(0x800fd5)

#unicorn_debugger.add_breakpoint(0x800992)
#unicorn_debugger.add_breakpoint(0x800fc0)

unicorn_debugger.add_breakpoint(BASE + 0x40099d)

unicorn_debugger.add_breakpoint(BASE + 0x400996)

unicorn_debugger.hook_instruction("cpuid", {
		"EBX":0x756e6547,
		"EDX":0x49656e69,
		"ECX":0x6c65746e
})


unicorn_debugger.trace_registers("EFLAGS")

unicorn_debugger.add_breakpoint(BASE + 0x400dc5, "check_mem")


'''
	-	with this hook, the correct path is taken

	-	what instruction messes with the eflags ;(

unicorn_debugger.hook_instruction("0x800dcc", {
		"EFLAGS":514
	})
'''

#pretty_print_bytes(emulator.mem_read(BASE + 0x2b38b8 + 0x400dc5, 8))
#exit(0)


# callback for tracing basic blocks
def hook_block(uc, address, size, user_data):
    bold_print(">>> Tracing call block at 0x%x(%s), block size = 0x%x" % (address, unicorn_debugger.determine_location(address)  , size))
    print(uc.reg_read(UC_X86_REG_RBP))

def hook_mem_invalid(uc, access, address, size, value, user_data):
	bold_print(">>> Address hit {}({}), size {}".format(hex(address), unicorn_debugger.determine_location(address), size))

def hook_code(mu, address, size, user_data):  
	global unicorn_debugger
	try:
		print('>>> (%x) Tracing instruction at 0x%x (%s), instruction size = 0x%x' % (unicorn_debugger.instruction_count, address, unicorn_debugger.determine_location(address), size))
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


