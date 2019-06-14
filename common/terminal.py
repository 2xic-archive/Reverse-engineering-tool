

from elf.elf_parser import *
from .model import *


'''
	will write a parser, maybe ast. 
'''

def command_input():
	while True:
		print("term>	", end="")
		try:
			command = input("")
		except Exception as e:
			break
		print(command)

def go_text(binary):
	global target
	target = model(elf(sys.argv[1]), None)
	print("terminal view is like gdb")

	command_input()