from unicorn import *
from unicorn.x86_const import *
import os

class syscall_exception(Exception):
    pass

def hook_syscall32(mu, user_data):
	eax = mu.reg_read(UC_X86_REG_EAX)
	print(">>> got SYSCALL with EAX = 0x%x" %(eax))
	mu.emu_stop()

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

		end_index = 64 	+ 8
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("Linux", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("vultr.guest", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("4.9.0-8-amd64", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("#1 SMP Debian 4.9.110-3+deb9u6 (2018-10-08)", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("x86_64", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("(none)", 65))

	elif(rax == 0xc):
		old_brk = user_data.brk
		user_data.brk += mu.reg_read(UC_X86_REG_RBP)

		mu.reg_write(UC_X86_REG_RAX, user_data.brk)
		mu.reg_write(UC_X86_REG_RBX, old_brk)	
		mu.reg_write(UC_X86_REG_RCX, 0x400994)

	elif(rax == 0x9e):
		#	https://github.com/torvalds/linux/blob/6f0d349d922ba44e4348a17a78ea51b7135965b1/arch/x86/um/syscalls_64.c
		#	https://manpages.debian.org/unstable/manpages-dev/syscall.2.en.html

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
			raise syscall_exception("unknown call in syscall")
	
		mu.reg_write(UC_X86_REG_RAX, 0)
		mu.reg_write(UC_X86_REG_RCX, 0x400994)
		mu.reg_write(UC_X86_REG_R11, 0x246)
		'''
			-	something gets wrongly set.
			-	I think you have enougth info to fix it.
	
					-	need to fix WRMSR
		'''
	elif(rax == 0x59):
		#	http://man7.org/linux/man-pages/man2/readlink.2.html
		_bytes_, string = user_data.unicorn_debugger.read_2_null(rdi)

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

	elif(rax == 0x15):
		try:
			_bytes_, string = user_data.unicorn_debugger.read_2_null(rdi)			
			string = string[:-1] # remove \0

			#	https://unix.superglobalmegacorp.com/Net2/newsrc/sys/unistd.h.html
			mode = {
				0 	: "F_OK",# test for existence of file
				0x01: "X_OK",	# test for execute or search permission
				0x02: "W_OK",	# test for write permission
				0x04: "R_OK"	# test for read permission
			}
			mode = mode[rsi]
						
			results = None
			if(mode == "F_OK"):
				results = os.path.isfile(string)
			else:
				raise Exception("not implemented")

			if not results:
				mu.reg_write(UC_X86_REG_RAX, 0xfffffffffffffffe) # seems to be some bitwise operations, proably include that it does not exsist, therefore can't be excecuted or read.
													# (i got the value from gdb)
				mu.reg_write(UC_X86_REG_RCX, 0x400994)
				mu.reg_write(UC_X86_REG_R11, 0x346)
			else:
				raise Exception("not implemented")
#			user_data.unicorn_debugger.handle_commands(memory_access=True)
		except Exception as e:
			mu.emu_stop()
			print(e)
			pass	

	elif(rax == 0xe7):
		#	http://man7.org/linux/man-pages/man2/exit_group.2.html
		#	exit_group

		#	since we are a emulator, how much do we actually need to exit/ clean up?
		#	currently nothing :=)
		print("exit 0!")
		mu.emu_stop()
	else:
		mu.emu_stop()
		raise syscall_exception("unknown syscall(0x%x, %i). Fix!" % (rax, rax))

