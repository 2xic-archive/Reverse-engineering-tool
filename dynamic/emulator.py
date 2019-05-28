from unicorn import *
from unicorn.x86_const import *
from capstone import *
import struct

from .dynamic_linker import *
from elf.elf_parser import *
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
		self.vsdo_start = 0x2000000

	def push_string(self, string_list):
		for string in string_list:
			self.push_bytes(string + "\x00")

	def byte_string_with_length(self, input_string, length=0):
		start = bytearray(input_string.encode())
		# padding
		for i in range(len(input_string), length):
			start.append(0)
		if(start[length - 1] != 0):
			raise Exception("not null terminated string")
		return bytes(start)

	def push_bytes(self, bytes_array):
		rsp = self.emulator.reg_read(UC_X86_REG_RSP)
		rsp -= len(bytes_array)
		self.emulator.mem_write(rsp, bytes_array)
		self.emulator.reg_write(UC_X86_REG_RSP, rsp)
		assert(type(rsp) != None)
		return rsp

	def stack_insert_at_reverse_index(self, index, bytes_data):
		self.emulator.mem_write(self.stack_pointer + index, bytes_data)
		return (index + len(bytes_data))

	def add_zero_byte(self):
		return self.push_bytes(bytes(bytearray(1)))

	def hex_bytes(hex_string):
		return bytes(reversed(bytes(bytearray.fromhex(hex_string.replace("0x", "")))))
	
	def push_string(self, string):
		assert(type(string) == str)
		return self.push_bytes((string + "\0").encode())

	def random_prng_bytes(self, size=16):
		return bytes(bytearray(random.getrandbits(8) for _ in range(size)))

	def arch_align_stack(self):
		#	https://elixir.bootlin.com/linux/v3.18/source/arch/x86/kernel/process.c#L459
		sp = self.emulator.reg_read(UC_X86_REG_RSP)
		sp -= random.randint(0, 256) % 8192;
		sp &= ~0xf
		self.emulator.reg_write(UC_X86_REG_RSP, sp)
		return sp

	def stack_round(self, item):
		return ((15 + (self.stack_pointer)) + item) &~ 15

	def stack_set(self, value):
		self.emulator.reg_write(UC_X86_REG_RSP, value)

	def align_stack(self):
		#	https://elixir.bootlin.com/linux/v3.18/source/arch/x86/kernel/process.c#L459
		rsp = self.emulator.reg_read(UC_X86_REG_RSP)
		rsp &= ~0xf
		self.emulator.reg_write(UC_X86_REG_RSP, rsp)

	def init_stack(self):
		start = self.stack_pointer

		self.actual_location_exec = self.push_string("/root/test/test_binaries/static_small")
		self.actual_platform_location = self.push_string("x86_64")
		self.actual_location_prng = self.push_bytes(self.random_prng_bytes())

		self.setup_aux_vector()
		
		argc = 0
		envp = 1
		items = (argc + 1) + (envp + 1) + 1

		self.push_bytes(struct.pack("<Q", 0)) # null envp

		self.push_bytes(struct.pack("<Q", 0)) # null arg
		self.push_bytes(struct.pack("<Q", self.actual_location_exec)) # argc
		self.push_bytes(struct.pack("<Q", 1)) # argc

		end = self.stack_pointer
		delta = (start - end)
			
		return start, end, delta

	@property
	def stack_pointer(self):
		return self.emulator.reg_read(UC_X86_REG_RSP)


	def aux_entry(self, key_id, val):
		self.aux_vector.append((key_id, val))

	def setup_aux_vector(self):
		self.aux_vector = []
	
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

		self.aux_entry(self.AT_NULL, 0x0)

		self.aux_entry(self.AT_PLATFORM, self.actual_platform_location) 
		self.aux_entry(self.AT_EXECFN, self.actual_location_exec) 
		self.aux_entry(self.AT_RANDOM, self.actual_location_prng)	

		self.aux_entry(self.AT_SECURE, 0x0)		#	super secure
		self.aux_entry(self.AT_EGID, 0x500)
		self.aux_entry(self.AT_GID, 0x500)
		self.aux_entry(self.AT_EUID, 0x500)
		self.aux_entry(self.AT_UID, 0x500)

		self.aux_entry(self.AT_ENTRY, self.BASE + self.target.program_entry_point) 	
		self.aux_entry(self.AT_FLAGS, 0x0)		#	what are flags?
		self.aux_entry(self.AT_BASE, 0x0)

		self.aux_entry(self.AT_PHNUM, self.target.program_header_count)
		self.aux_entry(self.AT_PHENT, self.target.program_header_size)
		self.aux_entry(self.AT_PHDR, self.BASE + self.target.program_header_start)

		self.aux_entry(self.AT_CLKTCK, 100)
		self.aux_entry(self.AT_PAGESZ, self.ELF_EXEC_PAGESIZE)
		self.aux_entry(self.AT_HWCAP, 0x42424242)
		self.aux_entry(self.AT_SYSINFO_EHDR, self.vsdo_start)


		for key, value in self.aux_vector:
			# key value storage, in memory!
			self.push_bytes(bytes(bytearray(struct.pack("<Q", value))))
			self.push_bytes(bytes(bytearray(struct.pack("<Q", key))))

	@property
	def path(self):
		return os.path.dirname(os.path.realpath(__file__)) + "/"

	def setup_vsdo(self):
		self.emulator.mem_map(self.vsdo_start, 1024 * 1024)
		# currently loading this binary into memory... not the best way of doing things....
		self.emulator.mem_write(self.vsdo_start, open(self.path + "vsdo.bin", "rb").read())

class emulator(stack_handler):
	def __init__(self, target):
		super().__init__()

		self.target = target

		self.emulator = Uc(UC_ARCH_X86, UC_MODE_64)


		self.setup_vsdo()

		'''
			Program memory
		'''
		self.target = target
		self.BASE = 0x400000
		self.program_size =  1024 * 1024 * 8

		self.logging = False


		#	PAGE_ZERO
		self.emulator.mem_map(0, 0x400000)


		self.emulator.mem_map(self.BASE, self.program_size)
		self.emulator.mem_write(0x400000, self.target.file[:0x18f])
		self.load_binary_sections()

		'''
			stack memory
		'''
		stack_adr = 0x1200000
		stack_size =  (1024 * 1024 * 8) # 8 mb stack

		self.emulator.mem_map(stack_adr, stack_size)
		self.emulator.reg_write(UC_X86_REG_RSP, stack_adr + stack_size - 1)


		'''
			* Dynamic mapping will happen here *
				-	already coded part of the linker
				-	will have a static binary running before more work on dynamic
		'''

		address_space = {
			"stack":[stack_adr, stack_adr + stack_size],
			"program":[self.BASE, self.program_size]
		}

		self.unicorn_debugger = unicorn_debug(self.emulator, self.section_virtual_map, self.section_map, address_space, self.logging)
		self.unicorn_debugger.full_trace = True


		#	used to follow the same path as gdb
		#	I don't think this hook actually is needed to make the binary run "correctly"
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
			},
			5:{
				"RAX":0x1,
				"RBX":0x0,
				"RCX":0x4d,
				"RDX":0x2c307d
			}

			,
			6:{
				"RAX":0x1,
				"RBX":0x0,
				"RCX":0x4d,
				"RDX":0x2c307d
			},
			7:{
				"RAX":0x1,
				"RBX":0x0,
				"RCX":0x4d,
				"RDX":0x2c307d
			}

		},
			{
				"max_hit_count":7
			}
		)


		#	will actually hook xgetbv (since ecx will be zero and trying to hook on xgetbv will be to late....)
		self.unicorn_debugger.add_hook("0x400e01", {
			0:{
				"RAX":0x7,
				"RCX":0x0,
				"RDX":0x0,
				"RIP":0x400e06
			}
		},
			{
				"max_hit_count":0
			}
		)


#		self.unicorn_debugger.add_breakpoint(0x414253)#, "jump")
		self.unicorn_debugger.add_breakpoint(0x414253, "jump") #  qword [fs:rax], main_arena
		self.unicorn_debugger.add_breakpoint(0x43fede, "jump") # qword [fs:rcx], rdx
		self.unicorn_debugger.add_breakpoint(0x43fef0, "jump") # mov qword [fs:rcx], rdx
		self.unicorn_debugger.add_breakpoint(0x43fefb, "jump") # qword [fs:rdx], rax


		#	need to write back the value that should have been written at
		#	0x414253
		#	fs:
		self.unicorn_debugger.add_hook("0x4131e0", {
			0:{
				"RBX":0x6b2800
			}
		},
			{
				"max_hit_count":10
			}
		)
		#	fs:
		self.unicorn_debugger.add_hook("0x435ec3",{
			0:{
				#	just want to jump the instruction....
			}		
		},
			{
				"max_hit_count":3
			}
		)
		# fs:rax
		self.unicorn_debugger.add_hook("0x413bef", {
			0:{
				"RBX":0x6b2800	
			}
		},
			{
				"max_hit_count":0
			}
		)

		self.unicorn_debugger.add_hook("0x431757", {
			0:{
				"ymm0":"xmm0",
				"RIP":0x43175c # unicorn reports wrong size!
			}
		},
			{
				"max_hit_count":0
			}
		)

		# need to fix interface with [fs:rax]
		self.unicorn_debugger.add_hook("0x43febe", {
			0:{
				"RAX":0x6b39c0 
			}
		},
			{
				"max_hit_count":0
			}
		)

	def load_binary_sections(self):
		self.brk = 0x6b6000

		self.section_virtual_map = {
			
		}

		self.section_map = {
			
		}
		for name, content in (self.target.sections_with_name).items():
			self.section_map[name] = [ int(content["virtual_address"],16),  int(content["virtual_address"],16) + content["size"]]

			if(content["type_name"] == "SHT_NOBITS" or not "SHF_ALLOC" in content["flags"]):
				print("Skipped section %s (%s)" % (name, content["flags"]))
				continue

			if("SHF_WRITE" in content["flags"]):
				new_address = int(content["virtual_address"],16) + int(content["size"])
		#		if(self.brk < new_address):
		#			self.brk = new_address

			file_offset = content["file_offset"]
			file_end = file_offset + int(content["size"])
			section_bytes = self.target.file[file_offset:file_end]

			start = int(content["virtual_address"],16)
			end = int(content["virtual_address"],16) + int(content["size"])


			print("Loaded section %s at 0x%x -> 0x%x (%s)" % (name, start, end, content["flags"]))

			self.emulator.mem_write(int(content["virtual_address"],16), section_bytes)


			if(content["size"] > 0):
				self.section_virtual_map[name] = [start, end]		

	def log_text(self, text, style=None, level=0):
		if(self.logging):
			if(style == None):
				print(text)
			elif(style == "bold"):
				bold_print(text)

	def log_bold_text(self, text, level=0):
		return self.log_text(text, "bold", level)
	
#	@threaded
	def run(self):
		self.address_register = {

		}
		# callback for tracing basic blocks
		def hook_block(uc, address, size, user_data):
		    self.log_bold_text(">>> Tracing call block at 0x%x(%s), block size = 0x%x" % (address, self.unicorn_debugger.determine_location(address)  , size))
		    self.log_text(uc.reg_read(UC_X86_REG_RBP))

		def hook_mem_invalid(uc, access, address, size, value, user_data):
			self.log_bold_text(">>> Address hit {}({}), size {}".format(hex(address), self.unicorn_debugger.determine_location(address), size))

		def hook_code(mu, address, size, user_data):  
			try:
				self.log_text('>>> (%x) Tracing instruction at 0x%x  [0x%x] (%s), instruction size = 0x%x' % (self.unicorn_debugger.instruction_count, address, address-self.BASE, self.unicorn_debugger.determine_location(address), size))


				'''
					baisc yeah, the database will take over here(soon)...
				'''
				address_hex = hex(address-self.BASE)
				if(self.address_register.get(address_hex, None) == None):
					self.address_register[address_hex] = []
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
				print(e)
				bold_print("exception stop ....")
				print(e)
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				print(exc_type, fname, exc_tb.tb_lineno)

				exit(0)

		def hook_mem_access(uc, access, address, size, value, user_data):
			if access == UC_MEM_WRITE:
				self.log_bold_text(">>> Memory is being WRITE at 0x%x(%s), data size = %u, data value = 0x%x" %(address, self.unicorn_debugger.determine_location(address) , size, value))
			else:
				if(size > 32):
					self.log_bold_text(">>> Memory is being READ at 0x%x (%s), data size = %u" %(address, self.unicorn_debugger.determine_location(address),  size))
				else:
					try:
						self.log_bold_text(">>> Memory is being READ at 0x%x (%s), data size = %u , data value = %s" %(address, self.unicorn_debugger.determine_location(address),  size , pretty_print_bytes(uc.mem_read(address, size), logging=False)))	
					except Exception as e:
						self.log_bold_text(">>> Memory is being READ at 0x%x " %(address))

							
			self.unicorn_debugger.memory_hook_check(address, access == UC_MEM_WRITE)
			self.unicorn_debugger.check_memory_value(value)


		def hook_intr(uc, intno, user_data):
			if intno == 0x80:
				self.handle_linux_syscall()

		def hook_syscall(mu, user_data):
			eax = mu.reg_read(UC_X86_REG_EAX)
			self.log_text(">>> got SYSCALL with EAX = 0x%x" %(eax))
			mu.emu_stop()


		start, end, delta = self.init_stack()

#		view_stack(end, pretty_print_bytes(self.emulator.mem_read(end, delta), aschii=False))

		self.emulator.hook_add(UC_HOOK_INSN, hook_syscall64, self, 1, 0, UC_X86_INS_SYSCALL)
		self.emulator.reg_write(UC_X86_REG_RSP, end)

		self.emulator.hook_add(UC_HOOK_INTR, hook_intr)
		self.emulator.hook_add(UC_HOOK_MEM_INVALID, hook_mem_invalid)

		self.emulator.hook_add(UC_HOOK_MEM_WRITE, hook_mem_access)
		self.emulator.hook_add(UC_HOOK_MEM_READ, hook_mem_access)

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


