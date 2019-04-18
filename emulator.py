from unicorn import *
from unicorn.x86_const import *
from capstone import *
import struct

from dynamic_linker import *
from elf_parser import *



def bold_print(text):
	print('\033[1m' + text + '\033[0m')


target = elf("./hega")


emulator = Uc(UC_ARCH_X86, UC_MODE_64)


BASE = 0x400000
program_size =  1024*1024

emulator.mem_map(BASE, program_size)
emulator.mem_write(BASE, target.file)



stack_adr = 0x0
stack_size =  1024 * 1024

emulator.mem_map(stack_adr, stack_size)
emulator.reg_write(UC_X86_REG_RSP, stack_adr + stack_size - 1)


#	haven't integrated the dynamic linker yet!
emulator.mem_map(0x600000, 1024 * 1024)
emulator.mem_write(0x600fd8, bytes(bytearray.fromhex('deadbeef')))


'''
	reading libc
'''
libc = open("/lib/x86_64-linux-gnu/libc.so.6", "rb").read()
emulator.mem_map(0x800000, 1024 * 8192 )
emulator.mem_write(0x800000, libc)


#	having problems with the stack
#	maybe I found a bug?
	#	https://github.com/unicorn-engine/unicorn/issues/1083
emulator.mem_write(0xfffd8, bytes(bytearray.fromhex('deadbeef')))


address_space = {
	"stack":[stack_adr, stack_adr + stack_size],
	"program":[BASE, BASE + program_size],
	"random trampoline_sapce":[0x600000, 0x600000 + 1024* 1024],
	"libc":[0x800000,  1024 * 8192]
}



def get_insstruction(data):
	mode = Cs(CS_ARCH_X86, CS_MODE_64)
	string = ""
	for dissably in mode.disasm(data, 0x100):
		string += "%s %s;" % (dissably.mnemonic, dissably.op_str)
	return string

def determine_location(address):
	global address_space
	for location_name, address_location in address_space.items():
		if(address_location[0] <= address <= address_location[1]):
			return location_name
	return "unkown"


start_libc_c_program = 0x800000 + 0x201f0
frame_dummy_init_array_entry = 0x4006c9
frame_dummy = BASE + 0x630



# callback for tracing basic blocks
def hook_block(uc, address, size, user_data):
    print(">>> Tracing basic block at 0x%x(%s), block size = 0x%x" % (address, determine_location(address)  , size))


instruction_number = 0
def hook_code(mu, address, size, user_data):  
	global instruction_number
	print('\t>>> Tracing instruction at 0x%x (%s), instruction size = 0x%x' % (address, determine_location(address), size))
	try:
		print("\t %s" % (get_insstruction(bytes(mu.mem_read(address, size)))))
	except Exception as e:
		print(e)
	if(hex(address) == "0x400535"):
		mu.reg_write(UC_X86_REG_RIP, mu.reg_read(UC_X86_REG_RIP) + size)
	if(hex(address) == hex(0x400995)):
		mu.reg_write(UC_X86_REG_RIP, mu.reg_read(UC_X86_REG_RIP) + size)

	if(address == 0x400554 and False):
		'''
			call qword ptr [rip + 0x200a7e];
		'''

		'''
			calling the libc_start function

				first read the qword[hardcoded]
				push return address onto the stack.
				(both are hardcoded :=) )

		'''
		mu.reg_write(UC_X86_REG_RIP, start_libc_c_program)
		mu.mem_write(0xfffd8, hex_address(0x40055a))
		mu.reg_write(UC_X86_REG_RSP, mu.reg_read(UC_X86_REG_RSP) - 8)

	if(address == 0x4006c9):
		location = mu.reg_read(UC_X86_REG_R12)
		print(mu.mem_read(location, 8))
	
		if(bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00') == mu.mem_read(location, 8)):
			print("trampoline .... ")
			mu.reg_write(UC_X86_REG_RIP, frame_dummy)
		
	instruction_number += 1
	if(address == 0x0):
		exit(0)

	if(instruction_number > 1200):
		print("got stuck in loop ? increase 'instruction_number' if not")
		exit(0)


def hook_mem_access(uc, access, address, size, value, user_data):
	if access == UC_MEM_WRITE:
		bold_print(">>> Memory is being WRITE at 0x%x(%s), data size = %u, data value = 0x%x" %(address, determine_location(address) , size, value))
		if(address == 0xfffd8):
			print(uc.mem_read(0xfffd8, 8))
	else:
		bold_print(">>> Memory is being READ at 0x%x (%s), data size = %u" %(address, determine_location(address),  size))
		print(uc.mem_read(address, size))

def hook_mem_invalid(uc, access, address, size, value, user_data):
	bold_print("Address hit {}, size {}".format(hex(address), size))

emulator.hook_add(UC_HOOK_MEM_WRITE, hook_mem_access)
emulator.hook_add(UC_HOOK_MEM_READ, hook_mem_access)

emulator.hook_add(UC_MEM_READ_UNMAPPED, hook_mem_invalid)
emulator.hook_add(UC_ERR_READ_UNMAPPED, hook_mem_invalid)
emulator.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED, hook_mem_invalid)

emulator.hook_add(UC_HOOK_BLOCK, hook_block)
emulator.hook_add(UC_HOOK_CODE, hook_code)

if(target.program_entry_point < BASE):
	emulator.emu_start(BASE + target.program_entry_point, BASE + target.program_entry_point + 0x50)
else:
	emulator.emu_start(target.program_entry_point, target.program_entry_point + 0x50)


