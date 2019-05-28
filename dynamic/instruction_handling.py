

'''
	testing currently!!	
		-	need to implement WRMSR, unicorn does not handle MSR
	
		-	good info here
			-	https://github.com/unicorn-engine/unicorn/issues/718



	need to be able to map and EXECUTE this insturction into memory somehow.....
	
'''
ADDRESS = 0x1000000

def WRMSR(mu, address):
	global ADDRESS

	CODE = b"wrmsr"
	msr = 0xC0000100 


	rax = mu.reg_read(UC_X86_REG_RAX)
	rdx = mu.reg_read(UC_X86_REG_RDX)
#	rax = mu.reg_read(UC_X86_REG_RAX)

	#	https://www.felixcloutier.com/x86/wrmsr
		#	high-order 32 bits !

	RAX = rax & 0xFFFFFFFF
	RDX = rdx >> 32 & 0xFFFFFFFF
	RCX = msr & 0xFFFFFFFF

	#mu.mem_map(ADDRESS + 1024, 2 * 1024 * 1024)
	mu.mem_write(ADDRESS + 1024, CODE)
	mu.emu_start(ADDRESS + 1024, ADDRESS + 1024 + len(CODE))


from unicorn import *
from unicorn.x86_const import * 
from keystone import *
from capstone import *

def encode_instruction(CODE):
	try:
		ks = Ks(KS_ARCH_X86, KS_MODE_64)
		encoding, count = ks.asm(CODE)
	#	print("keystone instruction size: %i" % (len(encoding)))
		return bytes(encoding)
	except KsError as e:
		print("ERROR: %s" %e)
	return None


'''
	basic trampoline interface
		-	first you need to let the current instruction finish
		-	after that you have to move the RIP 
		-	run the trampoline instruction
		-	after that have finished you need to set the rip back
			to where it should have gone after finishing the first instruction


		-	like the code belows gets the job, but is it so "hard" to make unicorn run a custom instruction ?
			-	old me, there are better ways!
				-	thank you unicorn <3
		-	I think my trampoline code migth still be useful tho!
			-	time will tell...
'''

class trampoline:
	def __init__(self, unicorn):
		self.unicorn = unicorn
		self.jump_next_instruction = False
		self.patch_code_comming = False
		self.completed_patch_address = 0

		self.trampolines = {

		}
		self.enabled = False
	def add_trampoline_address(self, address):
		self.trampolines[address] = True

	def is_trampoline(self, address):
		return not (self.trampolines.get(address, None) == None)

	def add_patch(self):
		self.jump_next_instruction = True

	def add_anchor(self, address):
		self.jump_back_2 = address

	def completed_patch(self, address):
		self.completed_patch_address = address

	def check(self):
		if(self.enabled):
			if(self.jump_next_instruction):
				self.unicorn.reg_write(UC_X86_REG_RIP, 0)
				self.jump_next_instruction = False
				self.patch_code_comming = True
				return 0
			elif(self.patch_code_comming):
				self.patch_code_comming = 0
				return 1
			elif(self.completed_patch_address == self.unicorn.reg_read(UC_X86_REG_RIP)):
				self.unicorn.reg_write(UC_X86_REG_RIP, self.jump_back_2)
				self.completed_patch_address = None
				return 3
		return 2


count = 0
def hook_code(mu, address, size, user_data):  
	global count


	if(count > 10):
		print("force exit")
		mu.emu_stop()
		exit(0)

	count += 1




	check = user_data.check()
	if(check == 2):
		print("instruction size %i" % (size))
		print("RAX before %i" % (mu.reg_read(UC_X86_REG_RAX)))
		data = bytes(mu.mem_read(address, size))
		mode = Cs(CS_ARCH_X86, CS_MODE_64)


		'''
		if(user_data.is_trampoline(address)):
			user_data.add_patch()
			user_data.add_anchor(address + size)
		'''

		for dissably in mode.disasm(data, 0x100):
			#	if not patch_back:
			print(dissably.mnemonic + "\t" + dissably.op_str)

		print("unicorn instruction size %i" % (size))
	elif(check == 1):
		print("RAX before %i" % (mu.reg_read(UC_X86_REG_RAX)))
		user_data.completed_patch(address + size)
		print("running patched code...")
		data = bytes(mu.mem_read(address, size))
		mode = Cs(CS_ARCH_X86, CS_MODE_64)
		for dissably in mode.disasm(data, 0x100):
			print(dissably.mnemonic + "\t" + dissably.op_str)

	elif(check == 3):
		print("trampoline back ...")
	print("")

def run_test():
	UNICORN_CODE = encode_instruction("mov rax, 10; mov rax, 20")
	PATCH_CODE = encode_instruction("mov rax, 30")
	return UNICORN_CODE, PATCH_CODE



def run_fs():
	UNICORN_CODE = encode_instruction("mov eax, dword ptr fs:[rax];")
	PATCH_CODE = encode_instruction("mov rax, 30")
	return UNICORN_CODE, PATCH_CODE


def hook_mem_invalid(uc, access, address, size, value, user_data):
	print(size)
	print("0x%x , 0x%x" % (address, get_negative_val(address)))


import math

def get_bits(number):
	bits_count = int(math.log(abs(number), 2)) + 1
	bits = []
	for i in range(bits_count):
		#	read each bit out
		bits.append((number >> i) & 1)
	return bits[:-1]

def get_negative_val(input_num):
	num = 0
	for index, y in enumerate(get_bits(input_num)):
		y ^= 1
		num += y * (2 ** index)
	return int(num)

'''
	-	trying to get 
'''

# okay I found this after some resarch
	#	https://github.com/unicorn-engine/unicorn/commit/d331b8f7d819e647393bbfb060e06a8069992002
	#	thank you unicorn <3
SCRATCH_ADDR = 0x0
def set_msr(uc, msr, value, scratch=SCRATCH_ADDR):
	'''
	set the given model-specific register (MSR) to the given value.
	this will clobber some memory at the given scratch address, as it emits some code.
	'''
	# save clobbered registers
	orax = uc.reg_read(UC_X86_REG_RAX)
	ordx = uc.reg_read(UC_X86_REG_RDX)
	orcx = uc.reg_read(UC_X86_REG_RCX)
	orip = uc.reg_read(UC_X86_REG_RIP)

	# x86: wrmsr
	buf = b'\x0f\x30'
	uc.mem_write(scratch, buf)
	uc.reg_write(UC_X86_REG_RAX, value & 0xFFFFFFFF)
	uc.reg_write(UC_X86_REG_RDX, (value >> 32) & 0xFFFFFFFF)
	uc.reg_write(UC_X86_REG_RCX, msr & 0xFFFFFFFF)
	uc.emu_start(scratch, scratch+len(buf), count=1)

	# restore clobbered registers
	uc.reg_write(UC_X86_REG_RAX, orax)
	uc.reg_write(UC_X86_REG_RDX, ordx)
	uc.reg_write(UC_X86_REG_RCX, orcx)
	uc.reg_write(UC_X86_REG_RIP, orip)


def get_msr(uc, msr, scratch=SCRATCH_ADDR):
	'''
	fetch the contents of the given model-specific register (MSR).
	this will clobber some memory at the given scratch address, as it emits some code.
	'''
	# save clobbered registers
	orax = uc.reg_read(UC_X86_REG_RAX)
	ordx = uc.reg_read(UC_X86_REG_RDX)
	orcx = uc.reg_read(UC_X86_REG_RCX)
	orip = uc.reg_read(UC_X86_REG_RIP)

	# x86: rdmsr
	buf = b'\x0f\x32'
	uc.mem_write(scratch, buf)
	uc.reg_write(UC_X86_REG_RCX, msr & 0xFFFFFFFF)
	uc.emu_start(scratch, scratch+len(buf), count=1)
	eax = uc.reg_read(UC_X86_REG_EAX)
	edx = uc.reg_read(UC_X86_REG_EDX)

	# restore clobbered registers
	uc.reg_write(UC_X86_REG_RAX, orax)
	uc.reg_write(UC_X86_REG_RDX, ordx)
	uc.reg_write(UC_X86_REG_RCX, orcx)
	uc.reg_write(UC_X86_REG_RIP, orip)

	return (edx << 32) | (eax & 0xFFFFFFFF)

if(__name__ == "__main__"):
	test = False
	UNICORN_CODE, PATCH_CODE = None, None

	if(test):
		UNICORN_CODE, PATCH_CODE =	run_test()
	else:
		UNICORN_CODE, PATCH_CODE =	run_fs()


	try:
		mu = Uc(UC_ARCH_X86, UC_MODE_64)
		trampoline_checker = trampoline(mu)

		if(test):
			trampoline_checker.add_trampoline_address(ADDRESS)
		else:
			pass
	#		mu.mem_map(0x0,0x1000,3)
	#		mu.mem_map(0x1000,0x1000,3)
	#		mu.reg_write(UC_X86_REG_FS, 10)
	#		mu.reg_write(UC_X86_REG_GS,0x1800)


		mu.hook_add(UC_HOOK_MEM_INVALID, hook_mem_invalid)
		mu.hook_add(UC_HOOK_CODE, hook_code, trampoline_checker)
		# map 2MB memory for this emulation
		mu.mem_map(ADDRESS, 2 * 1024 * 1024)

		mu.mem_map(0, 1024 * 1024) # page with instruction jump code ? 
		mu.mem_write(0, PATCH_CODE)

		print("crash....")

		FSMSR = 0xC0000100
		set_msr(mu, FSMSR, 0x100)


		# write machine code to be emulated to memory
		mu.mem_write(ADDRESS, UNICORN_CODE)

		print("what is fs ? %i" % mu.reg_read(UC_X86_REG_FS))

		mu.emu_start(ADDRESS, ADDRESS + len(UNICORN_CODE))

		print("what is fs ? %i" % get_msr(mu, FSMSR))

#		mu.emu_start(ADDRESS, ADDRESS + len(UNICORN_CODE))
#		print(mu.reg_read(UC_X86_REG_RAX))
#		print(mu.reg_read(UC_X86_REG_FS))

	except UcError as e:
		print("ERROR: %s" % e)




