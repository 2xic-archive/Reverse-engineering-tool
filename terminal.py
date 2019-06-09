from elf.elf_parser import *
from static.assembler import *
from model import *
from elf.elf_parser_key_value import *

import time


'''
nasm -f elf64 small_binary.s -o small_binary.o
ld -s -o hello small_binary.o
'''


'''
static = elf("./test_binaries/hello")
dynamic = emulator(static)
dynamic.run()
'''


#static = elf("./test_binaries/static_small")
static = elf("./test_binaries/fibonacci")
print(static)

'''
test_hello = False
if not test_hello:
	static = elf("./test_binaries/static_small")
	dynamic = emulator(static)
	dynamic.run()
else:
	static = elf("./test_binaries/small_c_hello")
	dynamic = emulator(static)
	dynamic.run()
'''