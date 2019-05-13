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
from .syscall_handler import *


import threading
def threaded(function):
	def wrapper(*args, **kwargs):
		thread = threading.Thread(target=function, args=args, kwargs=kwargs)
		thread.start()
		return thread
	return wrapper

class emulator(syscalls):
	def __init__(self, target):
		super().__init__()

		self.emulator = Uc(UC_ARCH_X86, UC_MODE_64)


		'''
			I think my stack layout is wrong.

			https://elixir.bootlin.com/linux/v3.18/source/fs/binfmt_elf.c#L603

			I have should  have read some kernel code before. Here is some of the things i'm
			missing 

			https://elixir.bootlin.com/linux/v3.18/source/fs/binfmt_elf.c#L149

	
			https://github.com/torvalds/linux/blob/master/arch/x86/include/asm/elf.h
			

		'''


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
		self.target = target
		self.BASE = 0x400000
		self.program_size =  1024 * 1024 * 8

		self.emulator.mem_map(self.BASE, self.program_size)

		section_virtual_map = {
			
		}

		section_map = {
			
		}

		for name, content in (self.target.sections_with_name).items():
			section_map[name] = [ int(content["virtual_address"],16),  int(content["virtual_address"],16) + content["size"]]

			if(content["type_name"] == "SHT_NOBITS" or not "SHF_ALLOC" in content["flags"]):
				print("Skipped section %s" % (name))
				continue

			file_offset = content["file_offset"]
			file_end = file_offset + int(content["size"])
			section_bytes = self.target.file[file_offset:file_end]

			start = int(content["virtual_address"],16)
			end = int(content["virtual_address"],16) + int(content["size"])
			self.emulator.mem_write(int(content["virtual_address"],16), section_bytes)


			print("Loaded section %s at 0x%x -> 0x%x" % (name, start, end))

			if(name == ".rodata"):
				#print(section_bytes)
				print(hex(file_offset))
				pretty_print_bytes(self.target.file[0x8cac0:0x8cae0])
				pretty_print_bytes(self.emulator.mem_read(0x48cad8, 0x60))
#				assert(section_bytes == self.emulator.mem_read(self.BASE + int(content["virtual_address"],16), len(section_bytes)))
#				print(hex(self.BASE + int(content["virtual_address"],16)))
#				content = self.emulator.mem_read(self.BASE + int(content["virtual_address"],16), len(section_bytes))
#				print("dafak ? ")
#				pretty_print_bytes(content[:0x60])
#				pretty_print_bytes(self.emulator.mem_read(0x4894e0, 0x60))
#				pretty_print_bytes(section_bytes[:0x60])
				#	0x894e0-0x8cac0

				#print(hex(file_offset), hex(file_end))
#				exit(0)


	#			pretty_print_bytes(section_bytes)

			if(content["size"] > 0):
				section_virtual_map[name] = [start, end]


		'''
			stack memory
		'''
		stack_adr = 0x1200000
		stack_size =  (1024 * 1024 * 8) # 8 mb stack


		self.emulator.mem_map(stack_adr, stack_size)
		self.emulator.reg_write(UC_X86_REG_RSP, stack_adr + stack_size - 1)


		#self.emulator.mem_map(0x1a00000, 1024 * 1024)


		'''
			* Dynamic mapping will happen here *
				-	already coded part of the linker
				-	will have a static binary running before more work on dynamic
		'''

		address_space = {
			"stack":[stack_adr, stack_adr + stack_size],
			"program":[self.BASE, self.program_size]
		}



		self.unicorn_debugger = unicorn_debug(self.emulator, section_virtual_map, section_map, address_space)

		self.unicorn_debugger.full_trace = True


		self.unicorn_debugger.add_hook("cpuid", {
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

		self.unicorn_debugger.add_hook("0x400e01", {
			0:{
				"RAX":0x7,
				"RCX":0x0,
				"RDX":0x0,
				"RIP":0x400e06 #+ self.BASE
			}
		},
			{
				"max_hit_count":0
			}
		)

		'''
		self.unicorn_debugger.add_hook("0x434db0", {
			0:{
				"RAX":0x21,
				"RIP":0x434db3 #+ self.BASE
			}
		},
			{
				"max_hit_count":0
			}
		)
		'''

		'''



#		self.unicorn_debugger.add_breakpoint(0x834e8a)



	#	print(self.emulator.mem_read(0x48cad8, 8))
	#	exit(0)

		self.emulator.mem_write(0x48cad0, bytes(reversed(bytes(bytearray.fromhex("0xdeadbeef".replace("0x", ""))))))
		'''



		'''
			just hardcoded
		'''
		'''
		self.unicorn_debugger.add_hook("0x434e8a", {
			0:{
				"RIP":0x434e98 
			},
			1:{
				"RIP":0x435030
			}
		},
			{
				"max_hit_count":1
			}
		)

		self.unicorn_debugger.add_hook("0x434eba", {
			0:{
				"RIP":0x434e80 
			}
		},
			{
				"max_hit_count":0
			}
		)


		self.unicorn_debugger.add_hook("0x434e88", {
			0:{
				"RIP":0x434e8a 
			},
			1:{
				"RIP":0x434e8a
			}
		},
			{
				"max_hit_count":1
			}
		)
		'''




		'''
		self.unicorn_debugger.add_hook("0x434ebf", {
			0:{
				"RIP":0x4350dd 
			}
		},
			{
				"max_hit_count":0
			}
		)

		self.unicorn_debugger.add_hook("0x434ec8", {
			0:{
				"RIP":0x434eca 
			}
		},
			{
				"max_hit_count":0
			}
		)

		self.unicorn_debugger.add_hook("0x434ed4", {
			0:{
				"RIP":0x434ed6 
			}
		},
			{
				"max_hit_count":0
			}
		)


		self.unicorn_debugger.add_hook("0x434ee0", {
			0:{
				"RIP":0x434ee2 
			}
		},
			{
				"max_hit_count":0
			}
		)
		'''

		#self.unicorn_debugger.add_breakpoint(0x834e88)
		#self.unicorn_debugger.add_breakpoint(0x834dba)


		self.unicorn_debugger.add_breakpoint(0x800e01, "exit")
		#self.unicorn_debugger.trace_registers("RDI", pause=True)

		#self.unicorn_debugger.add_hook_memory(0x19ffed8, write_only=True)
		#self.unicorn_debugger.add_hook_memory(0x19ffecc, write_only=True)
		#self.unicorn_debugger.add_hook_memory(0x19ffed0, write_only=True) # seems to be this bad boy that makes evreything go out of bounds
		#self.unicorn_debugger.trace_registers("RDX", pause=True)

		#self.unicorn_debugger.add_value_search(0x19fffff)

		'''
			happens at the start of the program...
			rdx stores the rsp....
			mov rdx, r13 ?
		'''
		#	0x19fffff


		self.address_register = {

		}

	
#	@threaded
	def run(self):
		# callback for tracing basic blocks
		def hook_block(uc, address, size, user_data):
		    bold_print(">>> Tracing call block at 0x%x(%s), block size = 0x%x" % (address, self.unicorn_debugger.determine_location(address)  , size))
		    print(uc.reg_read(UC_X86_REG_RBP))

		def hook_mem_invalid(uc, access, address, size, value, user_data):
			bold_print(">>> Address hit {}({}), size {}".format(hex(address), self.unicorn_debugger.determine_location(address), size))

		def hook_code(mu, address, size, user_data):  
			#global self.unicorn_debugger
			try:
				print('>>> (%x) Tracing instruction at 0x%x  [0x%x] (%s), instruction size = 0x%x' % (self.unicorn_debugger.instruction_count, address, address-self.BASE, self.unicorn_debugger.determine_location(address), size))

				address_hex = hex(address-self.BASE)
				if(self.address_register.get(address_hex, None) == None):
					self.address_register[address_hex] = []

				if(address == 0x400e01):
					mu.emu_stop()

				'''
					baisc yeah, the database will take over here...
				'''
				current_state = {

				}
				for i in ["rax", "rip", "eflags", "rsp"]:
					if(i == "rip"):
						current_state[i]  = hex(mu.reg_read(eval("UC_X86_REG_{}".format(i.upper()))) - self.BASE)
					else:
						current_state[i]  = hex(mu.reg_read(eval("UC_X86_REG_{}".format(i.upper()))))

				self.address_register[address_hex].append(current_state)


				self.unicorn_debugger.tick(address, size)
			except  Exception as e:
				bold_print("exception stop ....")
				print(e)
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				print(exc_type, fname, exc_tb.tb_lineno)

				exit(0)

		def hook_mem_access(uc, access, address, size, value, user_data):
			#global self.unicorn_debugger
			if access == UC_MEM_WRITE:
				bold_print(">>> Memory is being WRITE at 0x%x(%s), data size = %u, data value = 0x%x" %(address, self.unicorn_debugger.determine_location(address) , size, value))
			else:
				if(size > 32):
					bold_print(">>> Memory is being READ at 0x%x (%s), data size = %u" %(address, self.unicorn_debugger.determine_location(address),  size))
				else:
					try:
						bold_print(">>> Memory is being READ at 0x%x (%s), data size = %u , data value = %s" %(address, self.unicorn_debugger.determine_location(address),  size , pretty_print_bytes(uc.mem_read(address, size))))	
					except Exception as e:
						bold_print(">>> Memory is being READ at 0x%x " %(address))

							
			self.unicorn_debugger.memory_hook_check(address, access == UC_MEM_WRITE)
			self.unicorn_debugger.check_memory_value(value)


		def hook_intr(uc, intno, user_data):
			if intno == 0x80:
				self.handle_linux_syscall()

		def hook_syscall(mu, user_data):
			eax = mu.reg_read(UC_X86_REG_EAX)
			print(">>> got SYSCALL with EAX = 0x%x" %(eax))
			mu.emu_stop()


		def init_stack(mu):
			mu.reg_write(UC_X86_REG_RSP, mu.reg_read(UC_X86_REG_RSP) - 1)
			#	argv is zero and envp also
			#	https://www.gnu.org/software/libc/manual/html_node/Program-Arguments.html
#			mu.reg_write(UC_X86_REG_RSP, mu.reg_read(UC_X86_REG_RSP) - 1)
#			mu.reg_write(UC_X86_REG_RSP, mu.reg_read(UC_X86_REG_RSP) - 1)
						


		#	writing fake args 
		stack_space = 64 
#		init_stack(self.emulator)
		self.emulator.mem_write(self.emulator.reg_read(UC_X86_REG_RSP) - stack_space, bytes(reversed(bytes(bytearray.fromhex("0x01".replace("0x", ""))))))
		self.emulator.reg_write(UC_X86_REG_RSP, self.emulator.reg_read(UC_X86_REG_RSP) - stack_space)

		self.emulator.reg_write(UC_X86_REG_EFLAGS, 0x202)

		self.emulator.hook_add(UC_HOOK_INTR, hook_intr)
#		self.emulator.hook_add(UC_HOOK_INSN, hook_syscall, None, 1, 0, UC_X86_INS_SYSCALL)

		self.emulator.hook_add(UC_ERR_WRITE_UNMAPPED, hook_mem_invalid)
		self.emulator.hook_add(UC_HOOK_MEM_INVALID, hook_mem_invalid)


		self.emulator.hook_add(UC_HOOK_MEM_WRITE, hook_mem_access)
		self.emulator.hook_add(UC_HOOK_MEM_READ, hook_mem_access)

		self.emulator.hook_add(UC_MEM_READ_UNMAPPED, hook_mem_invalid)
		self.emulator.hook_add(UC_ERR_READ_UNMAPPED, hook_mem_invalid)
		self.emulator.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED, hook_mem_invalid)

		self.emulator.hook_add(UC_HOOK_BLOCK, hook_block)
		self.emulator.hook_add(UC_HOOK_CODE, hook_code)

		self.unicorn_debugger.setup()
		try:
			self.emulator.emu_start(self.target.program_entry_point, self.target.program_entry_point + 0x50)
		except Exception as e:
			print(e)
			self.unicorn_debugger.log_file.close()

	def get_register_data(self, address):
		#	basic api, easy to integrate with the database.
		return self.address_register.get(address, [])


