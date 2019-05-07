





def readable_eflags(current_state):
	if(True):
		flags =	[
				[2,	0x0004,	"PF"],	 
				[4,	0x0010,	"AF"],	
				[6,	0x0040,	"ZF"],	
				[7,	0x0080,	"SF"],	
				[8,	0x0100,	"TF"],	
				[9,	0x0200,	"IF"],	
				[10,	0x0400,	"DF"],	
				[11,	0x0800,	"OF"]
			]
		enabled_string = ""

		for flag in flags:
			if( (current_state & flag[1]) >> flag[0]):
				enabled_string += flag[2] + " "
		return enabled_string



unicorn = open("/root/test/test_binaries/unicorn.log").read().split("\n")
gdb = open("/root/test/test_binaries/gdb.log").read().split("\n")


count = 0

#for i in range(3000):
#	if("0x400e08" in unicorn[i]):# and count == 0):
#		count += 1
#		continue

i = 0
j = 0
while i < len(unicorn) and j < len(gdb):
	if(unicorn[i].strip() == (gdb[j].strip().split(" ")[1]) or (unicorn[i].strip() == gdb[j].strip().split("\t")[0].split(" ")[-1] )):
		if("=>" in gdb[j]):
			print(((unicorn[i].strip(), gdb[j].strip().split(" ")[1] )))
		pass
	else:
		if("=>" in gdb[j]):
			if(unicorn[i].strip() == "0x400e06" and "0x400e03" in gdb[j]):
				j += 2
				continue

		#	print("")
			print(((unicorn[i].strip(), gdb[j].strip().split(" ")[1] )))
		#	print(((unicorn[i].strip(), gdb[j+2].strip().split(" ")[1] )))
		#	print(((unicorn[i+4].strip(), gdb[j+4].strip().split(" ")[1] )))
		#	exit(0)
	i += 1
	j += 1



#		else:
#			print("unicorn | gdb")
#			print(( ( (int(unicorn[i].strip().replace("0x", ""),16)) , (int(gdb[j].strip().split("\t")[0].split(" ")[-1].replace("0x", ""),16 ))) ) )			
#print("all good?")



'''
	(gdb) info registers sil
	sil            0x1	1	


'''