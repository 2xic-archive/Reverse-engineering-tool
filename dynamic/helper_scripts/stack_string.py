




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
#hex_2_string("0x4d414c4c	0x4f435f00", big=True)
#hex_2_string("0x7fffffffee19:	0x2f000000	0x746f6f72	0x7365742f	0x65742f74")
#hex_2_string("0x7fffffffee29:	0x625f7473	0x72616e69	0x2f736569	0x74617473")
#hex_2_string("0x7fffffffee39:	0x735f6369	0x6c6c616d")
#print("")

hex_2_string("0x7fffffffe978:	0x00451e6a	0x00000000	0x00000011	0x00000000")
hex_2_string("0x7fffffffe988:	0x00000005	0x00000000	0x00000001	0x00000000")
hex_2_string("0x7fffffffe998:	0x00002190	0x00000000	0x00000005	0x00000000")
hex_2_string("0x7fffffffe9a8:	0x00008802	0x00000000	0x00000000	0x00000000")
hex_2_string("0x7fffffffe9b8:	0x00000400	0x00000000	0x00000000	0x00000000")
hex_2_string("0x7fffffffe9c8:	0x5cee6c39	0x00000000	0x16030145	0x00000000")
hex_2_string("0x7fffffffe9d8:	0x5cee6c39	0x00000000	0x16030145	0x00000000")
hex_2_string("0x7fffffffe9e8:	0x5cee670d	0x00000000	0x16030145	0x00000000")
hex_2_string("0x7fffffffe9f8:	0x00000000	0x00000000	0x00000000	0x00000000")
hex_2_string("0x7fffffffea08:	0x00000000	0x00000000	0x006b2300	0x00000000")
hex_2_string("0x7fffffffea18:	0x004a6260	0x00000000	0x00489704	0x00000000")
hex_2_string("0x7fffffffea28:	0x0040d004	0x00000000	0x006b2300	0x00000000")
hex_2_string("0x7fffffffea38:	0xffffffff	0x00000000	0x00489704	0x00000000")













