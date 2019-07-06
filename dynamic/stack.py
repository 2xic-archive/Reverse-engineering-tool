import os
from unicorn.x86_const import *
import random
import struct

class stack_handler(object):
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

	def stack_write_at_index(self, index, bytes_data):
		self.emulator.mem_write(index, bytes_data)
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

		'''
		i'm testing over ssh, so having ssh on the stack makes it easier
		to debug with gdb.
		'''
		envp = list(reversed([

				"SSH_CONNECTION=127.0.01 49940 127.0.01 22",	
				"_=/usr/bin/gdb",
				"OLDP",
				"XDG_SESSION_ID=1369",
				"USER=root",
				"PWD=/root",
				"LINES=24",
				"HOME=/root",
				"SSH_CLIENT=127.0.01 49940 22",
				"SSH_TTY=/dev/pts/1",
				"COLUMNS=75",
				"MAIL=/var/mail/root",
				"SHELL=/bin/bash",
				"TERM=xterm-256color",
				"SHLVL=1",
				"LOGNAME=root",
				"XDG_RUNTIME_DIR=/run/user/0",
				"PATH=/root/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
			]))


		envp_location = [

		]

		self.actual_location_exec = self.push_string("/root/test/test_binaries/static_small")

		for envp_varaible in envp:
			envp_location.append(self.push_string(envp_varaible))

		self.actual_platform_location = self.push_string("x86_64")

		self.actual_location_prng = self.push_bytes(self.random_prng_bytes())


#		self.align_stack()
		self.setup_aux_vector()
#		self.push_bytes(struct.pack("<Q", 0))
#		self.push_bytes(struct.pack("<Q", 0))

		

		argc = 0
		envp = 1
		items = (argc + 1) + (envp + 1) + 1

		self.push_bytes(struct.pack("<Q", 0)) # null envp

		for envp_var_location in envp_location:
			self.push_bytes(struct.pack("<Q", envp_var_location)) 

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

		self.aux_entry(self.AT_ENTRY, self.base_program_address + self.target.program_entry_point) 	
		self.aux_entry(self.AT_FLAGS, 0x0)		#	what are flags?
		self.aux_entry(self.AT_BASE, 0x0)

		self.aux_entry(self.AT_PHNUM, self.target.program_header_count)
		self.aux_entry(self.AT_PHENT, self.target.program_header_size)
		self.aux_entry(self.AT_PHDR, self.base_program_address + self.target.program_header_start)

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
		#	currently loading this binary into memory... not the best way of doing things....
		#	since vsdo actually just is a shortcut for some syscalls you can do the same as WRMSR
		self.emulator.mem_write(self.vsdo_start, open(self.path + "vsdo.bin", "rb").read())
