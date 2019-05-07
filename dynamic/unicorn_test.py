from __future__ import print_function
from unicorn import *
from unicorn.x86_const import *

from unicorn_helper import *

from keystone import *




mode =  Ks(KS_ARCH_X86, KS_MODE_64)
encoding, count = mode.asm("cmp eax, 0x6;")


#exit(0)
	


X86_CODE32 = bytes(encoding )

#print(encoding)
#print(bytes(encoding))
#print(type(encoding))
#print(type(b'H\x83\xe4\xf0'))
#b'H\x83\xe4\xf0' # INC ecx; DEC edx
ADDRESS = 0x1000000



mu = Uc(UC_ARCH_X86, UC_MODE_64)
debug = unicorn_debug(mu, None, None, None)


def set_bits(value):
	n = 0
	val = 0
	while value:
		n += 1
		val += value
		value &= value-1
	print(val % 2 == 0)
	return n



print("Emulate i386 code")
try:
	mu.mem_map(ADDRESS, 2 * 1024 * 1024)

	# write machine code to be emulated to memory
	mu.mem_write(ADDRESS, X86_CODE32)

	mu.reg_write(UC_X86_REG_EFLAGS, 0x293)

	# initialize machine registers
	mu.reg_write(UC_X86_REG_ECX, 0x1234)
	mu.reg_write(UC_X86_REG_EDX, 0x7890)


	eflags = mu.reg_read(UC_X86_REG_EFLAGS)
	print(">>> eflags = 0x%x" % eflags)
	print(debug.readable_eflags(mu.reg_read(UC_X86_REG_EFLAGS)))
	print(mu.reg_read(UC_X86_REG_EAX))


	# emulate code in infinite time & unlimited instructions
	mu.emu_start(ADDRESS, ADDRESS + len(X86_CODE32))

	print("=" * 16)

	eflags = mu.reg_read(UC_X86_REG_EFLAGS)
	print(">>> eflags = 0x%x" % eflags)
	print(debug.readable_eflags(mu.reg_read(UC_X86_REG_EFLAGS)))

except UcError as e:
	print("ERROR: %s" % e)





print(set_bits(0x6 & 0xFF) % 2 == 0)


'''
		parity flag checks
'''

'''
	http://www.c-jump.com/CIS77/ASM/Instructions/I77_0070_eflags_bits.htm


	maybe the reason is because of the stack size ? 



	okay, so problem with the eflags is because of the stack size. GR!
		-	not sure if this is a key problem tho
'''

'''
print(set_bits(140737488350240))
print(set_bits(140737488350240 & 0xFF))

#print(set_bits(1048560))
#print(set_bits(1048560 & 0xFF))


exit(0)
print(set_bits(0xfffffffffffffff0))


print(set_bits(0xfffffffffffffff0) % 2 == 0)
print(set_bits(0xfffffffffffffff0 & 0xFF) % 2 == 0)


print("gdb {}".format(debug.readable_eflags(0x202)))
print("before and unicorn {}".format(debug.readable_eflags(0x246)))
print("after and unicorn {}".format(debug.readable_eflags(0x206)))



exit(0)
'''