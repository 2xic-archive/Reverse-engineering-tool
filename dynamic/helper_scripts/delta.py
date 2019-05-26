'''
	used to debug unicorn against gdb
'''

unicorn = open("/root/test/test_binaries/unicorn.log").read().split("\n")
gdb = open("/root/test/test_binaries/gdb.log").read().split("\n")

i = 0
j = 0

hit_count = {
	"unicorn":{

	},
	"gdb":{

	}
}

while i < len(unicorn) and j < len(gdb):
	if("=>" in gdb[j]):
		results = hit_count["unicorn"].get(unicorn[i].strip(), 0)
		print(results)
		if(results == 0):
			hit_count["unicorn"][unicorn[i].strip()] = 1
			results = 1
		else:
			hit_count["unicorn"][unicorn[i].strip()] += 1
			results += 1
		#	unicorn[i].strip()

	if(unicorn[i].strip() == (gdb[j].strip().split(" ")[1]) or (unicorn[i].strip() == gdb[j].strip().split("\t")[0].split(" ")[-1] )):
		if("=>" in gdb[j]):
			print(((unicorn[i].strip(), gdb[j].strip().split(" ")[1] )))
		pass
	else:
		if("=>" in gdb[j]):
			if(unicorn[i].strip() == "0x400e06" and "0x400e03" in gdb[j]):
				j += 2
				print("stuck in loop?")
				continue
			if(unicorn[i].strip() == "0x400b3b" and "0x400b30" in gdb[j]):
				j += 3 * 2
				print("stuck in loop?")
				continue

			if(unicorn[i].strip() == "0x4142e0" and "0x41427d" in gdb[j]):
				#j += 3 * 2
				while not "0x4142e0" in gdb[j]:
					j += 1

				print("stuck in loop?")
				continue
			
			if(unicorn[i].strip() == "0x406cc5" and "0x406cdd" in gdb[j]):
				while not "0x406c96" in gdb[j]:
					j += 1
				i += 2
				print("stuck in loop?")
				continue

			if(unicorn[i].strip() == "0x417920" and "0x4178b6" in gdb[j]):
				while not "0x435741" in gdb[j]:
					j += 1

				while not "0x435741" in unicorn[i]:
					i += 1

#				i += 2
				print("stuck in loop?")
				continue

			if(unicorn[i].strip() == "0x4543d0" and "0x4541d5" in gdb[j]):
				while not "0x434763" in gdb[j]:
					j += 1

				while not "0x434763" in unicorn[i]:
					i += 1

#				i += 2
				print("stuck in loop?")
				continue
						
			
			print("error on line")
			print(((unicorn[i].strip(), gdb[j].strip().split(" ")[1] )))

#			results = hit_count["unicorn"].get(unicorn[i].strip(), None)
#			print(results)


			print(hex(i))
			exit(0)
		else:
			print("mismatch reg value....")
			print(unicorn[i])
			print(gdb[j])
	#		exit(0)
	i += 1
	j += 1

