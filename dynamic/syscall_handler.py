


from unicorn import *
from unicorn.x86_const import *


class syscalls:
	def print_buffer(self, memory_buffer):
		print("")
		for char in memory_buffer:
			print(chr(char), end="")
		print("")

	def handle_linux_syscall(self):
		eax = self.emulator.reg_read(UC_X86_REG_EAX)
		eip = self.emulator.reg_read(UC_X86_REG_EIP)

		ecx = self.emulator.reg_read(UC_X86_REG_ECX)
		edx = self.emulator.reg_read(UC_X86_REG_EDX)

		esi = self.emulator.reg_read(UC_X86_REG_ESI)
		edi = self.emulator.reg_read(UC_X86_REG_EDI)

		ebp = self.emulator.reg_read(UC_X86_REG_EBP)

		if(eax == 1):
			self.emulator.emu_stop()
		elif(eax == 4):
			memory_buffer = self.emulator.mem_read(self.BASE + ecx, edx)
			self.print_buffer(memory_buffer)
		else:
			raise Exception("un implemented syscalL!")



def hook_syscall32(mu, user_data):
	eax = mu.reg_read(UC_X86_REG_EAX)
	print(">>> got SYSCALL with EAX = 0x%x" %(eax))
	mu.emu_stop()

class syscall_exception(Exception):
    pass

def hook_syscall64(mu, user_data):
	rax = mu.reg_read(UC_X86_REG_RAX)
	rdi = mu.reg_read(UC_X86_REG_RDI)
	rsi = mu.reg_read(UC_X86_REG_RSI)
	rdx = mu.reg_read(UC_X86_REG_RDX)
	
	if(rax == 0x3f):
		#	http://man7.org/linux/man-pages/man2/uname.2.html 
		#	http://man7.org/linux/man-pages/man2/syscall.2.html

		mu.reg_write(UC_X86_REG_RAX, 0)
		mu.reg_write(UC_X86_REG_RCX, 0x400994)
		mu.reg_write(UC_X86_REG_R11, 0x306)
		mu.reg_write(UC_X86_REG_DL, 0x4)


#		end_index = user_data.stack_insert_at_reverse_index(12 + 64, user_data.byte_string_with_length("", 64))
		end_index = 64 	+ 8 #+ 16
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("Linux", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("vultr.guest", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("4.9.0-8-amd64", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("#1 SMP Debian 4.9.110-3+deb9u6 (2018-10-08)", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("x86_64", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("(none)", 65))

	elif(rax == 0xc):
		#mu.reg_write(UC_X86_REG_RAX, user_data.brk)
		old = user_data.brk
		user_data.brk += mu.reg_read(UC_X86_REG_RBP)

		mu.reg_write(UC_X86_REG_RAX, user_data.brk)

		mu.reg_write(UC_X86_REG_RBX, old)
		
		mu.reg_write(UC_X86_REG_RCX, 0x400994)

	elif(rax == 0x9e):

		#	https://github.com/torvalds/linux/blob/6f0d349d922ba44e4348a17a78ea51b7135965b1/arch/x86/um/syscalls_64.c

		#	https://manpages.debian.org/unstable/manpages-dev/syscall.2.en.html


	#	print(mu.reg_read(UC_X86_REG_RDI))
	#	print(mu.reg_read(UC_X86_REG_RSI))
	#	print(mu.reg_read(UC_X86_REG_RDX))

		code = mu.reg_read(UC_X86_REG_RDI)
		adress = mu.reg_read(UC_X86_REG_RSI)

		ARCH_SET_GS = 0x1001
		ARCH_SET_FS = 0x1002
		ARCH_GET_FS = 0x1003
		ARCH_GET_GS = 0x1004

		if(code == ARCH_SET_GS):
		#	mu.reg_write(UC_X86_REG_GS, adress)
			pass
		elif(code == ARCH_SET_FS):
		#	mu.reg_write(UC_X86_REG_FS, adress)
			pass
		elif(code == ARCH_GET_FS):
			pass
		elif(code == ARCH_GET_GS):
			pass
		else:
			raise syscall_exception("unkown call in syscall")

#		mu.reg_write(UC_X86_REG_RAX, 0)
#		mu.reg_write(UC_X86_REG_RCX, 0x400994)
	
		mu.reg_write(UC_X86_REG_RAX, 0)
		mu.reg_write(UC_X86_REG_RCX, 0x400994)
		mu.reg_write(UC_X86_REG_R11, 0x246)


		'''
			-	something gets wrongly set.
			-	I think you have enougth to fix it.

		'''
	#	mu.emu_stop()
	#	exit(0)

	elif(rax == 0x59):
		#	http://man7.org/linux/man-pages/man2/readlink.2.html




		bytes_, string = user_data.unicorn_debugger.read_2_null(rdi)

		if("/proc/self/exe" in string):
			location_string = "/root/test/test_binaries/static_small"
			end_index = user_data.stack_insert_at_reverse_index(0, user_data.byte_string_with_length(location_string, 45))

			mu.reg_write(UC_X86_REG_RAX, len(location_string))
			mu.reg_write(UC_X86_REG_RCX, 0x400994)

		else:
			print(hex(rdi))
			print(hex(rsi))
			print(hex(rdx))
			user_data.unicorn_debugger.handle_commands(memory_access=True)
			mu.emu_stop()
	else:
#		print(hex(user_data.brk))
#		print(mu.reg_read(UC_X86_REG_RBX))

		mu.emu_stop()
		raise syscall_exception("unkown syscall. Fix!")


		'''
		user_data.push_string_with_length("(none)", 64)

		user_data.push_string_with_length("x86_64", 64)

		user_data.push_string_with_length("#1 SMP Debian 4.9.110-3+deb9u6 (2018-10-08)", 64)

		user_data.push_string_with_length("4.9.0-8-amd64", 64)

		user_data.push_string_with_length("vultr.guest", 64)

		user_data.push_string_with_length("Linux", 64)

		user_data.push_string_with_length("", 64)
		'''

#		user_data.peek_stack()
#		exit(0)

#		print(user_data)
#		exit(0)

#		rax            0x0	0
#		rcx            0x400994	4196756
#		r11            0x306	774


#	self.handle_linux_syscall()
	'''
	rax = mu.reg_read(UC_X86_REG_RAX)
	rdi = mu.reg_read(UC_X86_REG_RDI)

	print(">>> got SYSCALL with RAX = %d" %(rax))

	mu.emu_stop()
	'''

