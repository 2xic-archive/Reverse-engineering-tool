
import os
from unicorn.x86_const import *
import random
import struct

class registers(object):
	def __init__(self):
		self.kernel_2_init()

	def kernel_2_init(self):
		#	http://asm.sourceforge.net/articles/startup.html#re0
		registers_value = {
			"EAX" :	0x0,
			"EBX" :	0x0,
			"ECX" :	0x0,
			"EDX" :	0x0,
			"ESI" :	0x0,
			"EDI" :	0x0,
			"EBP" :	0x0,
#			"ESP":	0xBFFFFB40
			"EFLAGS":	0x292,
			"CS" :	0x23,
			"DS" :	0x2B,
			"ES" :	0x2B,
			"FS" :	0x0,
			"GS" :	0x0,
			"SS" :	0x2B
		}

		for reigster, register_value in registers_value.items():
			self.emulator.reg_write(eval("UC_X86_REG_{}".format(reigster.upper())), register_value)
