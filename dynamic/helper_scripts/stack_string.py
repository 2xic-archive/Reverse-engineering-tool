
import struct
def	hex_2_string(input_stirng,	big=False):
	if(":"	in	input_stirng):
		input_stirng = input_stirng.split(":")[1]

	for string in input_stirng.split("\t"):
		if(len(string) == 0):
			continue
		hex_int = int(string, 16)
		#	endianness <3 
		if(big):
			bytes_string = struct.pack('>I', hex_int) # big-endian
		else:
			bytes_string = struct.pack('<I', hex_int) # little-endian
			
		results = []
		for byte in bytes_string:
			results.append(chr(byte))
			if(byte == 0):
				results.append("\n")
		try:
			print("".join(results), end="")
		except Exception as e:
			print("*ERROR* : ".format(input_stirng))
#	print("")

if __name__ == "__main__":
#	pass
#	hex_2_string("0x7fffffffee43:	0x62696c2f	0x3638782f	0x2d34365f	0x756e696c	0x6e672d78	0x696c2f75	0x732e6362	0x00362e6f")#	0x00000000")
	hex_2_string("0x62696c2f	0x3638782f	0x2d34365f	0x756e696c")
#	python3 ./dynamic/helper_scripts/stack_string.py

#	hex_2_string("0x7ffff7ffed60:	0x00000000	0x00000000	0x62696c2f	0x3638782f")
#	hex_2_string("0x7ffff7ffed70:	0x2d34365f	0x756e696c	0x00000000	0x00000000")
#	hex_2_string("0x2f756e67	0x2d78756e	0x696c2d34	0x365f3638",	big=False)
	print("")
