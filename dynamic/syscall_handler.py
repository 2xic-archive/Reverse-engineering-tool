from unicorn import *
from unicorn.x86_const import *
import os
from collections import OrderedDict 
from .unicorn_helper import pretty_print_bytes
import struct

class syscall_exception(Exception):
    pass

def hook_syscall32(mu, user_data):
	eax = mu.reg_read(UC_X86_REG_EAX)
	print(">>> got SYSCALL with EAX = 0x%x" %(eax))
	mu.emu_stop()

def syscall_info(mu):
	print("Syscall at 0x%x" % (mu.reg_read(UC_X86_REG_RIP)))

def hook_syscall64(mu, user_data):
	rax = mu.reg_read(UC_X86_REG_RAX)
	rdi = mu.reg_read(UC_X86_REG_RDI)
	rsi = mu.reg_read(UC_X86_REG_RSI)
	rdx = mu.reg_read(UC_X86_REG_RDX)

	r8 = mu.reg_read(UC_X86_REG_R8)
	r9 = mu.reg_read(UC_X86_REG_R9)
	r10 = mu.reg_read(UC_X86_REG_R10)
	

	rsp = mu.reg_read(UC_X86_REG_RSP)

	#	https://filippo.io/linux-syscall-table/
	syscall_info(mu)

	if(rax == 0x3f):
		#	http://man7.org/linux/man-pages/man2/uname.2.html 
		#	http://man7.org/linux/man-pages/man2/syscall.2.html

		mu.reg_write(UC_X86_REG_RAX, 0)
		mu.reg_write(UC_X86_REG_RCX, 0x400994)
		mu.reg_write(UC_X86_REG_R11, 0x306)
		mu.reg_write(UC_X86_REG_DL, 0x4)

		end_index = 64 + 8
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("Linux", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("vultr.guest", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("4.9.0-8-amd64", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("#1 SMP Debian 4.9.110-3+deb9u6 (2018-10-08)", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("x86_64", 65))
		end_index = user_data.stack_insert_at_reverse_index(end_index, user_data.byte_string_with_length("(none)", 65))

		user_data.add_syscall(["uname"])

	elif(rax == 0xc):
		old_brk = user_data.brk
		user_data.brk += mu.reg_read(UC_X86_REG_RBP)

		mu.reg_write(UC_X86_REG_RAX, user_data.brk)
		mu.reg_write(UC_X86_REG_RBX, old_brk)	
		mu.reg_write(UC_X86_REG_RCX, 0x400994)

		user_data.add_syscall(["brk", hex(mu.reg_read(UC_X86_REG_RBP))])

	elif(rax == 0x9):
		# mmap
		address = rdi
		length = rsi
		protection = rdx
		flags = r10
		file_descripor = r8
		off = r9

		print("implement mmap")
		mu.emu_stop()

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
#			import os
			location_string = user_data.target.file_path
#			print(user_data.target.file_path)
#			print(location_string)
#			print(os.path.abspath(user_data.target.file_path))
#			mu.emu_stop()
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
			_, string = user_data.unicorn_debugger.read_2_null(rdi)			
			string = string[:-1] # remove \0

			#	https://unix.superglobalmegacorp.com/Net2/newsrc/sys/unistd.h.html
			mode = {
				0 	: "F_OK",	# test for existence of file
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
		except Exception as e:
			mu.emu_stop()
			print(e)	

	elif(rax == 0x5):
		'''
		from http://man7.org/linux/man-pages/man2/stat.2.html

			struct stat {
			   dev_t     st_dev;         /* ID of device containing file */		
			   ino_t     st_ino;         /* Inode number */
			   mode_t    st_mode;        /* File type and mode */ 		 
			   nlink_t   st_nlink;       /* Number of hard links */
			   uid_t     st_uid;         /* User ID of owner */
			   gid_t     st_gid;         /* Group ID of owner */
			   dev_t     st_rdev;        /* Device ID (if special file) */
			   off_t     st_size;        /* Total size, in bytes */
			   blksize_t st_blksize;     /* Block size for filesystem I/O */
			   blkcnt_t  st_blocks;      /* Number of 512B blocks allocated */

			   /* Since Linux 2.6, the kernel supports nanosecond
				  precision for the following timestamp fields.
				  For the details before Linux 2.6, see NOTES. */

			   struct timespec st_atim;  /* Time of last access */
			   struct timespec st_mtim;  /* Time of last modification */
			   struct timespec st_ctim;  /* Time of last status change */

		   #define st_atime st_atim.tv_sec      /* Backward compatibility */
		   #define st_mtime st_mtim.tv_sec
		   #define st_ctime st_ctim.tv_sec
		   };
		'''

		'''

		fstat(3, {st_dev=makedev(254, 1), 
				st_ino=38776, 
				st_mode=S_IFREG|0755, 
				st_nlink=1, st_uid=0, 
				st_gid=0, 
				st_blksize=4096, 
				st_blocks=3304, 
				st_size=1689360, 
				st_atime=2019-06-15T21:17:01+0000.080974880, 
				st_mtime=2019-02-06T21:17:41+0000, 
				st_ctime=2019-03-29T20:30:59+0000.180000000}) = 0
			example syscall output from strace
				-	
		'''


		#	1	Standard output	STDOUT_FILENO	stdout
		#	this is what i'm calling with when trying Hello world, fd will be one
		#	fd from 0 to 2 is actually predefined.

		file_descripor = rdi 
		strcuture = rsi

		fstat_structure = OrderedDict()
		if(file_descripor == 1):
			file_stat = os.stat(file_descripor)
			# the fstat have a given tructure, you need to push in the correct order. Value only.
			fstat_structure["st_dev"] = file_stat.st_dev
			fstat_structure["st_ino"] = file_stat.st_ino
			fstat_structure["st_mode"] = file_stat.st_mode
			fstat_structure["st_nlink"] = file_stat.st_nlink
			fstat_structure["st_uid"] = file_stat.st_uid
			fstat_structure["st_gid"] = file_stat.st_gid
			fstat_structure["st_rdev"] = file_stat.st_rdev
			fstat_structure["st_size"] = file_stat.st_size
			fstat_structure["st_blksize"] = file_stat.st_blksize
			fstat_structure["st_blocks"] = file_stat.st_blocks
			fstat_structure["st_atime"] = int(file_stat.st_atime)
			fstat_structure["st_mtime"] = int(file_stat.st_mtime)
			fstat_structure["st_ctime"] = int(file_stat.st_ctime)
			fstat_structure["st_atime_nano"] = int(file_stat.st_atime)
			fstat_structure["st_mtime_nano"] = int(file_stat.st_mtime)
			fstat_structure["st_ctime_nano"] = int(file_stat.st_ctime)
		else:
			print("unknown file_descripor, not fully implemented yet")
			mu.emu_stop()
		
		#	print(strcuture)
		#	print(file_descripor)
		#	print(user_data.emulator.mem_read(strcuture, 128))

#		user_data.unicorn_debugger.view_stack(strcuture, pretty_print_bytes(user_data.emulator.mem_read(strcuture, 100), aschii=False))

#		user_data.unicorn_debugger.view_stack(rsp, pretty_print_bytes(user_data.emulator.mem_read(rsp, len(fstat_structure.items()) * 16), aschii=False))
		strcuture_index = strcuture

		#	maybe there should be a method to write qwords to the stack... cleaner maybe
#		print(fstat_structure)
		for key, value in fstat_structure.items():
			strcuture_index = user_data.stack_write_at_index(strcuture_index, bytes(bytearray(struct.pack("<Q", value))))

#		user_data.unicorn_debugger.view_stack(rsp, pretty_print_bytes(user_data.emulator.mem_read(rsp, len(fstat_structure.items()) * 16), aschii=False))
#		mu.emu_stop()


	elif(rax == 0xe7):
		#	http://man7.org/linux/man-pages/man2/exit_group.2.html
		#	exit_group

		#	since we are a emulator, how much do we actually need to exit/ clean up?
		#	currently nothing :=)
		user_data.add_syscall(["exit", hex(mu.reg_read(UC_X86_REG_RBP))])
		print("normal exit")
		mu.emu_stop()
	else:
		mu.emu_stop()
		raise syscall_exception("unknown syscall(0x%x, %i). Fix!" % (rax, rax))

