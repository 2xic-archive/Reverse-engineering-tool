


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