
import sys
import os
import json

PATH = (os.path.dirname(os.path.abspath(__file__)) + "/")

def load_break_points(libc_offset=0x7ffff7a3a000, ld_offset=0x7ffff7dd9000):
	break_adress = [

	]
	for breaks in json.loads(open(PATH + "../breaks.json", "r").read()):
		def parse(token):
			if(token == "ld"):
				return ld_offset
			elif(token == "ld_entry"):
				return ld_offset + ld.program_entry_point
			elif(token == "libc"):
				return libc_offset
			elif(token.isdigit()):
				return int(token)
			elif("0x" in token):
				return int(token, 16)
			return 0
		
		sign = 1
		break_location = 0
		token =""
		for y in breaks:
			if(y == "+" or y == "-"): 
				break_location += parse(token) * sign
				sign = (1) if(y == "+") else (-1)
				token = ""
				continue				
			token += y

		break_location += parse(token) * sign
		break_adress.append(break_location)
		print(breaks)
	return break_adress

hit_counts = 9

