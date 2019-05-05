from unicorn import *
from unicorn.x86_const import *
from capstone import *
import struct

from dynamic_linker import *
from elf.elf_parser import *



read_file = open("/lib/x86_64-linux-gnu/libc.so.6", "rb").read()
target = elf("/lib/x86_64-linux-gnu/libc.so.6")

target_start = None
target_end = None
for name, content in (target.sections_with_name).items():
	if(content["size"] > 0 and content["virtual_address"] == '0x0'):	
		print((name, content["virtual_address"]))
		print(content["size"])	

#	if(name == ".data"):
#		print(name)
#		target_start = int(content["file_offset"])
#		target_end = target_start + int(content["size"])


exit(0)
results = (read_file[target_start + 0x558: target_start + 0x558 + 8])
print(''.join('{:02x}'.format(x) for x in results ))


window_section = read_file[target_start:target_end]

#	okay all good
results = (window_section[0x558:0x558 + 8])
print(''.join('{:02x}'.format(x) for x in results ))


#	hm....
#	LOL that dada is of couse loaded from the .bss 

#	.bss starts at 0x39a700, and the target is 0x39ac20
#	0x39ac20- 0x39a700 = 0x520

bss_target = target.sections_with_name[".bss"]
offset = bss_target["file_offset"]
bss_window = read_file[offset:offset + bss_target["size"]]




#results = (window_section[0x558+0x5704:0x558+0x5704 + 8])
#print(results)
#print(''.join('{:02x}'.format(x) for x in results ))


#print(window_section)

#results = (read_file[target_start + 0x1ba0: target_start+0x1ba0 + 8])
#print(''.join('{:02x}'.format(x) for x in results ))


'''
	(notes continue from emulator)

	okay so the .data section starts at 0x399080
	the qword I want is at 0x3995d8
	delta 0x3995d8-0x399080 = 0x558


	okay, but what I want is the pointer ? 

	well 39ac20 is not in memory ...


	0x39ac20-0x3995d8 = 0x1648

	OKAY so now I have all I need? I just read the file offset + 0x558 + 0x1648 ?
	that should be all zero tho,


	what. when I read the file it is not zero. it has the value 20616c7761797320
	
	that was very strange 

'''