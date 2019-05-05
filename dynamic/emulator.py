from unicorn import *
from unicorn.x86_const import *
from capstone import *
import struct

from dynamic_linker import *
from elf.elf_parser import *
from .helpful_linker import *
import time


# 	https://www.cs.stevens.edu/~jschauma/631/elf.html

def bold_print(text):
	print('\033[1m' + text + '\033[0m')

def pretty_print_bytes(results):
	print(''.join('{:02x}'.format(x) for x in results ))
	return ''.join('{:02x}'.format(x) for x in results )
#target = elf("./mess/static_test_file")

#target = elf("./mess/jump_2_start")



#	this actually works ...
	#	I guess the migth have to be with something else ...
#target = elf("./test_binaries/for_loop_dynamic")

target = elf("./test_binaries/for_loop_dynamic")



emulator = Uc(UC_ARCH_X86, UC_MODE_64)


'''
	Program memory
'''
BASE = 0x400000
program_size =  1024 * 1024 * 4

emulator.mem_map(BASE, program_size)
#emulator.mem_write(BASE, target.file)

target_start = None
target_end = None

executed_count = 0
read_bytes = 0


for i in range(2):
	for name, content in (target.sections_with_name).items():
		file_offset = content["file_offset"]
		file_end = file_offset + int(content["size"])
		emulator.mem_write(BASE + int(content["virtual_address"],16), target.file[file_offset:file_end])
		executed_count += 1
		read_bytes += len(target.file[file_offset:file_end])
	time.sleep(2)

#	if(content["type"] == 0):
#		print(content["type"])
#		print(file_offset, file_end)
#exit(0)

print(executed_count)
print(read_bytes)
print(BASE + target.program_entry_point)
printed = pretty_print_bytes(emulator.mem_read(BASE + target.program_entry_point, 8))



#if(printed != "31ed4989d15e4889"):
#	for i in range(10):
#		printed = pretty_print_bytes(emulator.mem_read(BASE + target.program_entry_point, 8))
#		time.sleep(2)
'''
	sometimes the memory wont be read correctly?
'''
exit(0)

'''
	strange thing... I need to run the code above to map the binary the correct way, however
	it seems to make things unstable...

		maybe some memory has to get zeroed out or something ?

'''

'''
	stack memory

'''
stack_adr = 0x0
stack_size =  1024 * 1024

emulator.mem_map(stack_adr, stack_size)
emulator.reg_write(UC_X86_REG_RSP, stack_adr + stack_size - 1)


'''
	tramponline space
'''
tramponline_space = 0x600000
tramponline_size = 1024 * 1024
#	emulator.mem_map(0x600000, tramponline_size)


libc_start = 0x800000
libc_size = 1024 * 8192 

start_libc_c_program = 0x800000 + 0x201f0
start_frame_dummy = 0x400000 + 0x630
malloc_libc = 0x800000 + 0x7af10
libc_exit = (0x800000 + 0x35980)

emulator.mem_map(libc_start, libc_size )


emulator.mem_write(0xb98e40, bytes(reversed(bytes(bytearray.fromhex(hex(malloc_libc).replace("0x", ""))))))
emulator.mem_write(0xb958d8, bytes(reversed(bytes(bytearray.fromhex(hex(libc_exit).replace("0x", ""))))))
emulator.mem_write(0x800000 + 0x5704 + 0x1995d8,  bytes(reversed(bytes(bytearray.fromhex("0xdeadbeef".replace("0x", ""))))))

#	trampoline
emulator.mem_write(0x600fd8, bytes(reversed(bytes(bytearray.fromhex(hex(start_libc_c_program).replace("0x", ""))))))
emulator.mem_write(0x600e08, bytes(reversed(bytes(bytearray.fromhex(hex(start_frame_dummy).replace("0x", ""))))))




'''

	you know what makes me sad? glibc dosen't have all I need. I actually have to load a static binary to get to some functions
	like _dl_fini. GRR!

		-	how should I fix this when we are removing evreything that is hardcoded? 

'''

static_helper_start = 0x1500000
emulator.mem_map(static_helper_start, libc_size )
emulator.mem_write(static_helper_start, open("./test_binaries/static_helper", "rb").read())

#print(emulator.mem_read(libc_start + 12168224, 8))
#xit(0)

'''
	reading libc
'''

libc_target = elf("/lib/x86_64-linux-gnu/libc.so.6")

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
target_start = None
target_end = None
for name, content in (libc_target.sections_with_name).items():
	if(name == ".bss"):
		continue
	file_offset = content["file_offset"]
	file_end = file_offset + int(content["size"])
	emulator.mem_write(libc_start + int(content["virtual_address"],16), libc_target.file[file_offset:file_end])



bss = libc_target.sections_with_name[".text"]
file_offset = bss["file_offset"]
#virital_delta = 0x39ac20 - int(bss["virtual_address"], 16) 
#print(virital_delta)
def get_insstruction(data):
	mode = Cs(CS_ARCH_X86, CS_MODE_64)
	string = ""
	for dissably in mode.disasm(data, 0x100):
		string += "%s %s;\n" % (dissably.mnemonic, dissably.op_str)
	return string


laod_static = True
if(laod_static):
	static_target = elf("./test_binaries/static_helper")
	target_start = None
	target_end = None
	for name, content in (static_target.sections_with_name).items():
		if(name == ".bss"):
			continue
		file_offset = content["file_offset"]
		file_end = file_offset + int(content["size"])
		emulator.mem_write(static_helper_start + int(content["virtual_address"],16), static_target.file[file_offset:file_end])
#	pretty_print_bytes(emulator.mem_read(static_helper_start + 0x469d40, 8))
#	exit(0)
import time
time.sleep(1)



address_space = {
	"stack":[stack_adr, stack_adr + stack_size],
	"program":[BASE, BASE + program_size],
	"random trampoline_sapce":[tramponline_space, tramponline_space + tramponline_size],
	"libc":[libc_start, libc_start + libc_size],
	"static helper":[static_helper_start, static_helper_start + libc_size]
}





def determine_location(address):
	global address_space
	for location_name, address_location in address_space.items():
		if(address_location[0] <= address and address <= address_location[1]):
			return location_name
	return "unkown"


frame_dummy_init_array_entry = 0x4006c9
frame_dummy = BASE + 0x630



# callback for tracing basic blocks
def hook_block(uc, address, size, user_data):
    bold_print("	HIT CALL >>> Tracing basic block at 0x%x(%s), block size = 0x%x" % (address, determine_location(address)  , size))
    print(uc.reg_read(UC_X86_REG_RBP))

instruction_number = 0

#print(mu.reg_read())

address_hits = {
	
}

def hook_code(mu, address, size, user_data):  
	global instruction_number, address_hits, libc_start
	try:
		print('\t>>> (%x) Tracing instruction at 0x%x (%s), instruction size = 0x%x' % (instruction_number, address, determine_location(address), size))
		instruction = "fake"
		try:
			print("\t %s" % (get_insstruction(bytes(mu.mem_read(address, size)))))
			instruction = get_insstruction(bytes(mu.mem_read(address, size)))
			mu.mem_write(0xfffd8, bytes(bytearray.fromhex('40055a')))
		#	print(mu.mem_read(0xfffd8, 8))
		except Exception as e:
			print(e)
		#	stuck on wrong loop?
		if(address_hits.get(address) == None):
			address_hits[address] = 1
		else:
			address_hits[address] += 1

	
		instruction_number += 1



		if(0x83588b == address):
			target = mu.reg_read(UC_X86_REG_RCX)

			bytes_data = bytes(reversed(bytes(bytearray.fromhex("0x00000004".replace("0x", "")))))
			mu.mem_write(target, bytes_data)



		if(address == 0x8358bb):
			print("OKAY?")
#			print(mu.reg_read(UC_X86_REG_RAX))
			mu.reg_write(UC_X86_REG_RAX, 0)

		if(address == 0x8358e0):
			'''
				cheating to the end...
			'''
			mu.reg_write(UC_X86_REG_RIP, static_helper_start + 0x432630)

		if(address == 0x835878):
			print("you will crash on this instruction if you dont fix your bugs")
			print(hex(mu.reg_read(UC_X86_REG_R13)))
			results = 	mu.mem_read(0x835980 + 0x8, 8)


			print(''.join('{:02x}'.format(x) for x in results ))


			data = mu.reg_read(UC_X86_REG_R13)

			print("target == {}".format(data))
		



			if(data < 12168224):
				bytes_data = bytes(reversed(bytes(bytearray.fromhex("0x00000001".replace("0x", "")))))
	
				mu.mem_write(libc_start + data, bytes_data)
				mu.mem_write(libc_start + data + 0x8, bytes_data)


			
		#		print(mu.mem_read(mu.reg_read(UC_X86_REG_R13) + 8, 8))
			
				mu.reg_write(UC_X86_REG_R13, libc_start + data)


				pretty_print_bytes(mu.mem_read(mu.reg_read(UC_X86_REG_R13) + 0x8, 8))
			else:
				#mu.mem_write(data + 0x8, bytes_data)
				mu.reg_write(UC_X86_REG_R13, data + 0x8)
				pass

		if(0x83586a == address):
			print(hex(mu.reg_read(UC_X86_REG_RBP)))

			results = (mu.mem_read(mu.reg_read(UC_X86_REG_RBP), 16))
			print(''.join('{:02x}'.format(x) for x in results ))
			
			#	0x00100000
			print("just hardcode it, thanks gdb!")
	
		if(address == 0x835895):
	
			print(hex(mu.reg_read(UC_X86_REG_RCX)))
			target = mu.reg_read(UC_X86_REG_RCX)



		if(address == 0x835929):
			'''
			1: x/i $pc
			=> 0x7ffff7a6f929 <__run_exit_handlers+217>:	mov    0x18(%rax),%rdx
			(gdb) stepi
			83	in exit.c
			1: x/i $pc
			=> 0x7ffff7a6f92d <__run_exit_handlers+221>:	mov    0x20(%rax),%rdi
			'''
			target = mu.reg_read(UC_X86_REG_RAX) + 0x18
			print(mu.mem_read(target, 8))
			print(target)
	#		exit(0)

		if(address == 0x83593e):
			mu.reg_write(UC_X86_REG_RDX, 0x6f4 + 0x400000)



		if(address == 0x8358e0):
			print(hex(mu.reg_read(UC_X86_REG_RBP)))

		if(address == (0x800000 + 0x3586a)):
			pass
		

		if(address == 0x83586e):
			print("okay so what is the actual value?")
			results = mu.reg_read(UC_X86_REG_R13)
			#(emulator.mem_read(mu.reg_read(UC_X86_REG_RBP) - 0x200d69, 24))
			#print(''.join('{:02x}'.format(x) for x in results ))
	#		results2 = emulator.mem_read(0x800000 + 0x1995d8, 8)

			print('{:x}'.format(results))
	#		print('{:x}'.format(results2))

			print("is this because of the erorr from the qwords ? I wounder")

			#exit(0)

	#	if(address == 0x835878):

	#		print()

	#		exit(0)


		if(address == (0x800000 + 0x35873)):
			print("you are awinner")
		#	exit(0)

		if(address == 0x0):
			print("__NULL_PTR")
			exit(0)

		if(instruction_number > 0x150):
			print("got stuck in loop ? increase 'instruction_number' if not")
			for addr, hits in address_hits.items():
				if(hits > 10):
					#	makes it easy to loop-up!
					print((hex(addr - 0x800000), hits))
	#		print(address_hits)
			exit(0)

		if(address == 0x835878):
			print("new place...")
			pretty_print_bytes(mu.mem_read(mu.reg_read(UC_X86_REG_R13) + 0x8, 8))

#			exit(0)

	except  Exception as e:
		bold_print("exception stop ....")
		print(e)
		exit(0)

def hook_mem_access(uc, access, address, size, value, user_data):
	global instruction_number

	if access == UC_MEM_WRITE:
		bold_print(">>> Memory is being WRITE at 0x%x(%s), data size = %u, data value = 0x%x" %(address, determine_location(address) , size, value))
	else:
		if(address == 0xb995d8):
			print("all good?")
			print(hex(uc.reg_read(UC_X86_REG_RIP)))
			if(0x83586a == uc.reg_read(UC_X86_REG_RIP)):
				print("yes")
			else:
				print("no")
				exit(0)
	#	print(hex(uc.reg_read(UC_X86_REG_RSP)))
		bold_print(">>> Memory is being READ at 0x%x (%s), data size = %u" %(address, determine_location(address),  size))
		hex_string = "".join("%02x" % b for b in uc.mem_read(address, 8))
		return True

def hook_mem_invalid(uc, access, address, size, value, user_data):
	bold_print("Address hit {}, size {}".format(hex(address), size))

#	writing fake args 
emulator.reg_write(UC_X86_REG_RSP, emulator.reg_read(UC_X86_REG_RSP) - 8)

emulator.hook_add(UC_ERR_WRITE_UNMAPPED, hook_mem_invalid)
emulator.hook_add(UC_HOOK_MEM_INVALID, hook_mem_invalid)


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


