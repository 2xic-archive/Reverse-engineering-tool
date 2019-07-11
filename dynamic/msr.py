

from unicorn import *
from unicorn.x86_const import *

# okay I found this after some resarch
	#	https://github.com/unicorn-engine/unicorn/commit/d331b8f7d819e647393bbfb060e06a8069992002
	#	thank you unicorn <3
class msr_helper(object):
	def __init__(self):
		self.FSMSR = 0xC0000100
		self.scratch = 0x0

		self.set_msr(self.emulator, self.FSMSR, 0x1000)

	def set_msr(self, uc, msr, value):
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
		uc.mem_write(self.scratch, buf)
		uc.reg_write(UC_X86_REG_RAX, value & 0xFFFFFFFF)
		uc.reg_write(UC_X86_REG_RDX, (value >> 32) & 0xFFFFFFFF)
		uc.reg_write(UC_X86_REG_RCX, msr & 0xFFFFFFFF)
		uc.emu_start(self.scratch, self.scratch+len(buf), count=1)

		# restore clobbered registers
		uc.reg_write(UC_X86_REG_RAX, orax)
		uc.reg_write(UC_X86_REG_RDX, ordx)
		uc.reg_write(UC_X86_REG_RCX, orcx)
		uc.reg_write(UC_X86_REG_RIP, orip)


	def get_msr(self, uc, msr):
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
		uc.mem_write(self.scratch, buf)
		uc.reg_write(UC_X86_REG_RCX, msr & 0xFFFFFFFF)
		uc.emu_start(self.scratch, self.scratch+len(buf), count=1)
		eax = uc.reg_read(UC_X86_REG_EAX)
		edx = uc.reg_read(UC_X86_REG_EDX)

		# restore clobbered registers
		uc.reg_write(UC_X86_REG_RAX, orax)
		uc.reg_write(UC_X86_REG_RDX, ordx)
		uc.reg_write(UC_X86_REG_RCX, orcx)
		uc.reg_write(UC_X86_REG_RIP, orip)

		return (edx << 32) | (eax & 0xFFFFFFFF)



