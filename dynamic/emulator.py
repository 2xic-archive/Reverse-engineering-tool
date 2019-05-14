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

import random

import threading
def threaded(function):
	def wrapper(*args, **kwargs):
		thread = threading.Thread(target=function, args=args, kwargs=kwargs)
		thread.start()
		return thread
	return wrapper





class stack_handler():
	def __init__(self):
		super().__init__()
		pass

	def push_string(self, string_list):
		for string in string_list:
			self.push_bytes(string + "\x00")

	def push_bytes(self, bytes_array):
		rsp = self.emulator.reg_read(UC_X86_REG_RSP)
		rsp -= len(bytes_array)
		self.emulator.mem_write(rsp, bytes_array)
		self.emulator.reg_write(UC_X86_REG_RSP, rsp)
		assert(type(rsp) != None)
		return rsp

	def add_zero_byte(self):
		return self.push_bytes(bytes(bytearray(1)))

	def hex_bytes(hex_string):
		return bytes(reversed(bytes(bytearray.fromhex(hex_string.replace("0x", "")))))
	
	'''
	def init_stack(self):
		# https://elixir.bootlin.com/linux/v3.18/source/fs/binfmt_elf.c#L298
		self.add_zero_byte() # argc
		#	push argv and envp
		self.push_string([])

		self.add_zero_byte()

		self.push_string([]) # envp

		self.add_zero_byte()
		self.add_zero_byte()
	'''

	def push_string(self, string):
		assert(type(string) == str)
		return self.push_bytes((string + "\0").encode())


	def random_prng_bytes(self, size=16):
		return bytes(bytearray(random.getrandbits(8) for _ in range(size)))

	def init_stack(self):
		start = self.stack_pointer
		print("Stack starts here {}".format(hex(start)))

		self.push_bytes(bytes(12))

#		self.actual_location_exec = self.push_string("./simple")
#		self.actual_platform_location = self.push_string("x86_64")
		self.actual_location_prng = self.push_bytes(self.random_prng_bytes())

		self.align_stack()


		self.setup_aux_vector()

		self.push_bytes(struct.pack("<I", 0xdeadbeef)) # program name ;)

		self.push_bytes(struct.pack("<I", 0)) # no ergv
		self.push_bytes(struct.pack("<I", 0)) # no argv

		self.push_bytes(struct.pack("<I", 1)) # psuh argc

#		self.align_stack()

		end = self.stack_pointer
		print("Stack ends here {}".format(hex(end)))
		delta = (start - end)

#		pretty_print_bytes(self.emulator.mem_read(end, delta))

		print(delta)
			
		return start, end, delta

	def align_stack(self):
		#	https://elixir.bootlin.com/linux/v3.18/source/arch/x86/kernel/process.c#L459
		rsp = self.emulator.reg_read(UC_X86_REG_RSP)
		rsp &= ~0xf
		self.emulator.reg_write(UC_X86_REG_RSP, rsp)

	@property
	def stack_pointer(self):
		return self.emulator.reg_read(UC_X86_REG_RSP)


	def stack_round(self, item):
		return ((15 + (self.stack_pointer)) + item) &~ 15

	def aux_entry(self, key_id, val):
		self.aux_vector.append([key_id, val])

	def setup_aux_vector(self):
		self.aux_vector = []
		self.elf_info = []

		#	https://elixir.bootlin.com/linux/v3.18/source/include/uapi/linux/auxvec.h#L11
		self.AT_NULL  =   0	#end of vector 
		self.AT_IGNORE =  1	 # entry should be ignored 
		self.AT_EXECFD =  2	 # file descriptor of program 
		self.AT_PHDR  =   3	 # program headers for program 
		self.AT_PHENT =   4	 # size of program header entry 
		self.AT_PHNUM =   5	 # number of program headers 
		self.AT_PAGESZ =  6	 # system page size 
		self.AT_BASE  =   7	 # base address of interpreter 
		self.AT_FLAGS =   8	 # flags 
		self.AT_ENTRY =   9	 # entry point of program 
		self.AT_NOTELF =  10	 # program is not ELF 
		self.AT_UID    =  11	 # real uid 
		self.AT_EUID  =   12	 # effective uid 
		self.AT_GID   =   13	 # real gid 
		self.AT_EGID   =  14	 # effective gid 
		self.AT_PLATFORM  = 15  # string identifying CPU for optimizations 
		self.AT_HWCAP   = 16    # arch dependent hints at CPU capabilities 
		self.AT_CLKTCK =  17	 # frequency at which times() increments 
		self.AT_SECURE  = 23    # secure mode boolean */
		self.AT_BASE_PLATFORM = 24	 # string identifying real platform, may differ from AT_PLATFORM. 
		self.AT_RANDOM = 25	 # address of 16 random bytes 
		self.AT_HWCAP2 = 26	 # extension of AT_HWCAP 
		self.AT_EXECFN = 31	 # filename of program 

		self.AT_SYSINFO = 32
		self.AT_SYSINFO_EHDR = 33


		self.ELF_EXEC_PAGESIZE = 4096

		self.aux_entry(self.AT_SYSINFO, 0x0) # hardware capabilites ? 
		self.aux_entry(self.AT_SYSINFO_EHDR, 0x0) # hardware capabilites ? 

		self.aux_entry(self.AT_HWCAP, 0x0) # hardware capabilites ? 
		self.aux_entry(self.AT_PAGESZ, self.ELF_EXEC_PAGESIZE)
		self.aux_entry(self.AT_CLKTCK, 100)
		self.aux_entry(self.AT_PHDR, self.BASE + self.target.program_header_start)
		self.aux_entry(self.AT_PHENT, self.target.program_header_size)
		self.aux_entry(self.AT_PHNUM, self.target.program_header_count)
		self.aux_entry(self.AT_BASE, 0x40000000)
		self.aux_entry(self.AT_FLAGS, 0)
		self.aux_entry(self.AT_ENTRY, self.target.program_entry_point)
		self.aux_entry(self.AT_UID, 0)
		self.aux_entry(self.AT_EUID, 0)
		self.aux_entry(self.AT_GID, 0)
		self.aux_entry(self.AT_EGID, 0)
		self.aux_entry(self.AT_SECURE, 0)

		'''


		'''
			
		self.aux_entry(self.AT_RANDOM, self.actual_location_prng)
#		self.aux_entry(self.AT_EXECFN, self.actual_location_exec)
#		self.aux_entry(self.AT_PLATFORM, self.actual_platform_location)
		self.aux_entry(self.AT_NULL, 0)

		for key_val in reversed(self.aux_vector):
			self.push_bytes(bytes(bytearray(struct.pack("<I", key_val[0]))))
			new_rsp = self.push_bytes(bytes(bytearray(struct.pack("<I", key_val[1]))))
			self.elf_info.append([hex(new_rsp), key_val[0], key_val[1]])

		self.align_stack()


	#	print(self.random_prng_bytes())
	#	exit(0)
		'''
		actual_location_prng = self.push_bytes(self.random_prng_bytes())

		self.emulator.mem_write(location_help_prng, struct.pack('>Q', actual_location_prng))

		actual_location_exec = self.push_string("./simple")
		self.emulator.mem_write(location_help_exec, struct.pack('>Q',actual_location_exec))


		actual_platform_location = self.push_string("x86_64")
		self.emulator.mem_write(location_help_platform, struct.pack('>Q',actual_platform_location))
		'''

		for index, key_value in enumerate(self.elf_info):
			print("{}	{}	->	{}({})".format(key_value[0], hex(key_value[1]), key_value[2], hex(key_value[2])))

		#	http://articles.manugarg.com/aboutelfauxiliaryvectors.html
		#	this was nice also

		'''
		aux_entry(AT_HWCAP, ELF_HWCAP);
		aux_entry(AT_PAGESZ, ELF_EXEC_PAGESIZE);
		aux_entry(AT_CLKTCK, CLOCKS_PER_SEC);
		aux_entry(AT_PHDR, load_addr + exec->e_phoff);
		aux_entry(AT_PHENT, sizeof(struct elf_phdr));
		aux_entry(AT_PHNUM, exec->e_phnum);
		aux_entry(AT_BASE, interp_load_addr);
		aux_entry(AT_FLAGS, 0);
		aux_entry(AT_ENTRY, exec->e_entry);
		aux_entry(AT_UID, from_kuid_munged(cred->user_ns, cred->uid));
		aux_entry(AT_EUID, from_kuid_munged(cred->user_ns, cred->euid));
		aux_entry(AT_GID, from_kgid_munged(cred->user_ns, cred->gid));
		aux_entry(AT_EGID, from_kgid_munged(cred->user_ns, cred->egid));
	 	aux_entry(AT_SECURE, security_bprm_secureexec(bprm));
		aux_entry(AT_RANDOM, (elf_addr_t)(unsigned long)u_rand_bytes);
		'''


class emulator(stack_handler, syscalls):
	def __init__(self, target):
		super().__init__()

		self.target = target

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


		#self.unicorn_debugger.add_breakpoint(0x834e88)
		#self.unicorn_debugger.add_breakpoint(0x834dba)



		self.unicorn_debugger.add_breakpoint(0x400b30)

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


	#	def init_stack(mu):
	#		mu.reg_write(UC_X86_REG_RSP, mu.reg_read(UC_X86_REG_RSP) - 1)
			#	argv is zero and envp also
			#	https://www.gnu.org/software/libc/manual/html_node/Program-Arguments.html
#			mu.reg_write(UC_X86_REG_RSP, mu.reg_read(UC_X86_REG_RSP) - 1)
#			mu.reg_write(UC_X86_REG_RSP, mu.reg_read(UC_X86_REG_RSP) - 1)
						


		#	writing fake args 
#		stack_space = 64 
#		self.add_zero_byte()
#		exit(0)
#		init_stack(self.emulator)
#		self.emulator.mem_write(self.emulator.reg_read(UC_X86_REG_RSP) - stack_space, bytes(reversed(bytes(bytearray.fromhex("0x01".replace("0x", ""))))))
#		self.emulator.reg_write(UC_X86_REG_RSP, self.emulator.reg_read(UC_X86_REG_RSP) - stack_space)
		start, end, delta = self.init_stack()


		print("hedaer count ;(")
		print(self.target.program_header_count)
		print(self.target.program_header_size)
		print("stack layout")

		def space_stack(end, string, length=8, count=4):
			current_string = ""
			jump_count = 0
			for index, char in enumerate(string):
				#print(char, end="")
				current_string += char
				if(len(current_string) == length):
					if(jump_count == 0):
						print("{}".format(hex(end)), end="	")

					print(current_string, end=" ")
					current_string = ""
					jump_count += 1
					
					if(jump_count % 4 == 0 and jump_count > 0):
						end += 16
						print("\n{}".format(hex(end)), end="	")
			print("")

		space_stack(end, pretty_print_bytes(self.emulator.mem_read(end, delta), aschii=False))
		print("Size {}".format(delta))




#		exit(0)
#		exit(0)
#		print(self.emulator.mem_read(end, delta))
#		exit(0)




	
#		print(hex(self.emulator.reg_read(UC_X86_REG_RSP)))
#		exit(0)

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


