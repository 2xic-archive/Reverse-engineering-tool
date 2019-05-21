from unicorn import *
from unicorn.x86_const import * 
from keystone import *

CODE = b"vmovd xmm0, esi;"
UNICORN_CODE = None
try:
	ks = Ks(KS_ARCH_X86, KS_MODE_64)
	encoding, count = ks.asm(CODE)
	print("keystone instruction size: %i" % (len(encoding)))
	UNICORN_CODE = bytes(encoding)
except KsError as e:
	print("ERROR: %s" %e)

hex_encoding = []
for j in encoding:
	hex_encoding.append(hex(j))
print(hex_encoding)
print(encoding)
print(bytes(encoding))

ADDRESS = 0x1000000
def hook_code(mu, address, size, user_data):  
	print("unicorn instruction size %i" % (size))
	mu.emu_stop()

try:
	mu = Uc(UC_ARCH_X86, UC_MODE_64)
	mu.hook_add(UC_HOOK_CODE, hook_code)
	# map 2MB memory for this emulation
	mu.mem_map(ADDRESS, 2 * 1024 * 1024)

	# write machine code to be emulated to memory
	mu.mem_write(ADDRESS, UNICORN_CODE)

	print("real movment %s" % hex(mu.reg_read(UC_X86_REG_RIP)))

	mu.emu_start(ADDRESS, ADDRESS + len(UNICORN_CODE))

	print("real movment %s" % hex(mu.reg_read(UC_X86_REG_RIP)))
except UcError as e:
	print("ERROR: %s" % e)



