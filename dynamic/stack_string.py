




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



#hex_2_string("0xffffee42")
#hex_2_string("0x616e6962	0x73656972	0x6174732f	0x5f636974")
#hex_2_string("0x6c616d73	0x0000006c	0x00000000	0x00000000")


#hex_2_string("49d933", big=True)
#hex_2_string("6d612d38")



'''
hex_2_string("0x756e694c	0x00000078	0x00000000	0x00000000")
hex_2_string("0x7fffffffe970:	0x6c757600	0x672e7274	0x74736575	0x00000000")
hex_2_string("0x7fffffffe9b0:	0x2e340000	0x2d302e39	0x6d612d38	0x00343664")

hex_2_string("0x7fffffffe9f0:	0x23000000	0x4d532031	0x65442050	0x6e616962")
hex_2_string("0x7fffffffea00:	0x392e3420	0x3031312e	0x642b332d	0x75396265")
hex_2_string("0x7fffffffea10:	0x32282036	0x2d383130	0x302d3031	0x00002938")

hex_2_string("0x7fffffffea30:	0x00000000	0x5f363878	0x00003436	0x00000000")
hex_2_string("0x7fffffffea70:	0x00000000	0x6f6e2800	0x0029656e	0x00000000")

hex_2_string("756e694c")
hex_2_string("00435d23")
hex_2_string("2e392e34")
'''

print("")
#hex_2_string("7838365f	36340050", big=True)


#	print("")
#hex_2_string("0x36387880	0x0034365f")

#hex_2_string("0x00000000	0x6f6f722f	0x65742f74	0x742f7473")
#hex_2_string("0x5f747365	0x616e6962	0x73656972	0x5300732f")

#hex_2_string("0x5f003232	0x73752f3d	0x69622f72	0x64672f6e")
#hex_2_string("0x4c4f0062	0x44575044	0x6f722f3d	0x742f746f")
#hex_2_string("0x00747365	0x5f474458	0x53534553	0x5f4e4f49")
#hex_2_string("0x313d4449	0x53550037	0x723d5245	0x00746f6f")

'''
hex_2_string("0x3d445750	0x6f6f722f	0x65742f74	0x742f7473")
hex_2_string("0x5f747365	0x616e6962	0x73656972	0x4e494c00")
hex_2_string("0x333d5345	0x4f480032	0x2f3d454d	0x746f6f72")
'''
'''
hex_2_string("0x53003232	0x545f4853	0x2f3d5954	0x2f766564")
hex_2_string("0x2f737470	0x4f430033	0x4e4d554c	0x31313d53")
hex_2_string("0x414d0034	0x2f3d4c49	0x2f726176	0x6c69616d")
hex_2_string("0x6f6f722f	0x48530074	0x3d4c4c45	0x6e69622f")
hex_2_string("0x7361622f	0x45540068	0x783d4d52	0x6d726574")
hex_2_string("0x3635322d	0x6f6c6f63	0x48530072	0x3d4c564c")
hex_2_string("0x4f4c0031	0x4d414e47	0x6f723d45	0x5800746f")
hex_2_string("0x525f4744	0x49544e55	0x445f454d	0x2f3d5249")
hex_2_string("0x2f6e7572	0x72657375	0x5000302f	0x3d485441")
hex_2_string("0x7273752f	0x636f6c2f	0x732f6c61	0x3a6e6962")
hex_2_string("0x7273752f	0x636f6c2f	0x622f6c61	0x2f3a6e69")
hex_2_string("0x2f727375	0x6e696273	0x73752f3a	0x69622f72")
hex_2_string("0x732f3a6e	0x3a6e6962	0x6e69622f	0x6f722f00")
hex_2_string("0x742f746f	0x2f747365	0x74736574	0x6e69625f")
hex_2_string("0x65697261	0x00732f73	0x00000000	0x00000000")
'''