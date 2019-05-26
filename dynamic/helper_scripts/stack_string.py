




import struct
def hex_2_string(input_stirng, big=False):
	if(":" in input_stirng):
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
		print("".join(results), end="")


#hex_2_string("0x4d414c4c	0x4f435f00")
hex_2_string("0x4d414c4c	0x4f435f00", big=True)


hex_2_string("0x7fffffffee19:	0x2f000000	0x746f6f72	0x7365742f	0x65742f74")
hex_2_string("0x7fffffffee29:	0x625f7473	0x72616e69	0x2f736569	0x74617473")
hex_2_string("0x7fffffffee39:	0x735f6369	0x6c6c616d")
print("")














