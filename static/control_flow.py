import hashlib
		 
class block:
	def __init__(self):
		self.instructions = []
		self.instruction_string = ""
		self.start = None
		self.end = None
 
	def add(self, instruction):
		if(self.start == None):
			self.start = int(instruction["address"].replace("0x", ""), 16)
		self.instructions.append(instruction)
		self.instruction_string += instruction["address"] + "\t" + instruction["instruction"] + instruction["argument"] + "\n"
		self.end =  int(instruction["address"].replace("0x", ""), 16)
 
	def reconstruct(self):
		self.instruction_string = ""
		for instruction in self.instructions:
			self.instruction_string += instruction["address"] + "\t" + instruction["instruction"] + instruction["argument"] + "\n"
 
	def __str__(self):
		hash_object = hashlib.md5(self.instruction_string.encode())
		return hash_object.hexdigest()
 
 
class relation:
	def __init__(self, from_node, to_node, relation_type=None):
		self.from_node = from_node
		self.to_node = to_node
		self.type = relation_type
 
	def __str__(self):
		return self.from_node + "->" + self.to_node
 
class cfg:
	def __init__(self, code):
		self.node_relation = {
 
		}
		self.visited_node = {
 
		}
		self.instruction = code
		#self.start_address = code[0]["address"]
		self.start_address = self.instruction[0]["address"]
		self.end_address = self.instruction[-1]["address"]
		self.blocks = []
		self.call_stack = []
 
	def in_scope(self, address):
		if(address[0].isalpha()):
			return False
		address = int(address, 16)

		return int(self.start_address, 16) <= address <= int(self.end_address, 16)

	def is_branch(self, code):
		return "jne" in code or "je" in code or "jmp" in code \
		or "ret" in code or "call" in code
 
	def get_block(self, start_address):
		for j in range(len(self.instruction)):
			if(self.instruction[j]["address"] == start_address):
				break
		return self.instruction[j:]
 
	def parse_code_block(self, start=None):
		if(start == None):
			start = self.instruction[0]["address"]

		self.visited_node[start] = True
 
		new_relations = []
		new_block = block()
 
		code_block = self.get_block(start)
		for i in range(len(code_block)):
			new_block.add(code_block[i])
			if(self.is_branch(code_block[i]["instruction"])):
				if("call" in code_block[i]["instruction"]):
					continue
				#	if not self.in_scope(code_block[i]["argument"]):
					#	print("huh")
				#		continue
				#	else:
					#	print(code_block[i])
#						print("bruh")
#				if("ret" in code_block[i]["instruction"]):
#					yield newb					

				if("jne" in code_block[i]["instruction"] or "je" in code_block[i]["instruction"] or "jmp" in code_block[i]["instruction"] ):
					if(self.in_scope(code_block[i]["argument"])):
						new_relations.append(relation(start, code_block[i]["argument"], "jumpted"))

				if("jne" in code_block[i]["instruction"] or "je" in code_block[i]["instruction"] ):
					new_relations.append(relation(start, code_block[i + 1]["address"], "followed"))
 				
				#if("call" in code_block[i]["instruction"]):
					#if(int(self.start_address, 16) < int(code_block[i]["address"], 16)):
				#	print(self.in_scope(code_block[i]["argument"]))
					#	print("maybe")
				#	print(code_block[i]["address"])
				#	print(code_block[i]["argument"])
				#	exit(0)
 				#if("call" in code_block[i]["instruction"]):



				yield new_block
 
				for node_relation in new_relations:
					source = node_relation.from_node
					target = node_relation.to_node
 
					if not str(node_relation) in self.node_relation.keys():
						self.node_relation[str(node_relation)] = [source, target, node_relation.type]
					 
					if target in self.visited_node.keys():
						continue
 
					for parsed_block in self.parse_code_block(target):
						yield parsed_block

					
				break
		yield new_block
 
 
	def clean_blocks(self):
		for blocks in self.blocks:
			blockStart = blocks.start
			blockEnd = blocks.end
 
			for other_blocks in self.blocks:
				start_blockStart = other_blocks.start
				start_blockEnd = other_blocks.end
			 
				overlap = (blockStart < start_blockEnd) and start_blockEnd < blockEnd 
			#	print(overlap)
			#   if not overlap:
			#       continue
				 
				if(blockEnd == start_blockEnd and start_blockStart !=blockStart):
					biggest_block = other_blocks if(blockStart > start_blockStart) else blocks
					small = blocks if(blockStart > start_blockStart) else other_blocks
 
					pop_instructions = []
					for i in range(len(biggest_block.instructions)):
						instruction = biggest_block.instructions[i]
						if(int(instruction["address"].replace("0x", ""), 16) >= small.start):
							pop_instructions.append(i)
	#               
					pop_count = 0
					for instruction_pop_index in pop_instructions:
						biggest_block.instructions.pop(instruction_pop_index - pop_count)
						pop_count += 1
 
					#   get the new code
					biggest_block.reconstruct()
 
					relations_to_remove = []
					for key, val in self.node_relation.items():
						if(val[0] == hex(biggest_block.start)):
							new_relation = relation(hex(biggest_block.start), (val[1]))
							self.node_relation[str(new_relation)] = [hex(biggest_block.start), (val[1])]
 
							relations_to_remove.append(key)             
 
					for node_relation in relations_to_remove:
						self.node_relation.pop(node_relation)
				#       print(node_relation)
 
					new_relation = relation(hex(biggest_block.start), hex(small.start))
					self.node_relation[str(new_relation)] = [hex(biggest_block.start), hex(small.start)]
				else:
					continue
 
 
	def store_blocks(self, target=None):
		for blocks in self.parse_code_block(target):
			self.blocks.append(blocks)
		
		found_all = False
		highest_address = None
		for j in self.blocks:
			if(j.end == int(self.end_address, 16)):
				found_all = True
				break
			if(highest_address == None or highest_address < j.end):
				highest_address = j.end

		if not found_all:
			real_highest = self.get_block(hex(highest_address))[1]["address"]
			return self.store_blocks(real_highest)

 
	def return_edge_map(self):
		dfs_edges = {
 
		}
		edge_type = {

		}
		for j in self.node_relation:
			from_node = j.split("->")[0]
			 
			if(from_node in dfs_edges.keys()):
				continue
 
			dfs_edges[from_node] = []
			edge_type[from_node] = []

			for i in self.node_relation:
				if(from_node in i.split("->")[0]):
					to_node = i.split("->")[1]
					dfs_edges[from_node].append(to_node)
					edge_type[from_node].append(self.node_relation[i][- 1])

#		print(edge_type)
		return dfs_edges, edge_type
 
	def return_node_code(self):
		code_nodes = {
 
		}
		for block in self.blocks:
			code_nodes[hex(block.start)] = block.instructions # block.instruction_string.split("\n")
		return code_nodes

#	helps for debugging :=)
def test_graphviz(input_cfg):
	from graphviz import Digraph

	print(input_cfg["code"]["0x400518"])
	
	grapth = Digraph()
	print(input_cfg)
	for node_key, node_value in input_cfg["code"].items():
		code = ""
		for code_block in node_value:
#			print(node_value)
			code += "%s\t%s\t%s\n" % (code_block["address"], code_block["instruction"], code_block["argument"])
		print(node_key)
		print(code)
		grapth.node(node_key, label=code)
	
	for node_key, node_value in input_cfg["edges"].items():
		for edges in node_value:
			grapth.edge(node_key, edges)
			print("{}->{}".format(node_key, edges))

	grapth.view()
#	input("press enter") 
	exit(0)


def make_cfg(code):
	#   based on some code from 
	 
	#   https://www.cs.rice.edu/~keith/pubs/TR02-399.pdf
	#   https://www.diericx.net/post/generating-avr-assembly-control-flow-graphs/
	 
	code_cfg = cfg(code)
	code_cfg.store_blocks()
	code_cfg.clean_blocks()
 
	dfs_edges, dfs_edges_type = code_cfg.return_edge_map()
	codebase = code_cfg.return_node_code()
#	test_graphviz({"edges":dfs_edges, "code":codebase, "flow":sorted(list(dfs_edges.keys()))})
#	exit(0)
	return test_hirachy({"edges":dfs_edges, "type":dfs_edges_type, "code":codebase, "flow":sorted(list(dfs_edges.keys())), 
		"start":code_cfg.start_address, "end":code_cfg.end_address})


def dfs_path(grapth, start, end):
	stack = [(start, [start])]

	while len(stack) > 0:
		(vertex, current_path) = stack.pop()
		if(vertex in grapth.keys()):
			for edges in (set(grapth[vertex]) - set(current_path)):
				if(edges == end):
					yield current_path + [edges]
				else:
					stack.append((edges, current_path + [edges]))

def test_hirachy(code):
	head = code["start"]
	code["hirachy"] = {

	}
	code["hirachy"][head] = 1
	zero_nodes = []

	highest_level = 0
	for j in code["code"].keys():
		if(j == head):
			continue
		size = 0
		for q in (dfs_path(code["edges"], head, j)):
			if(len(q) > size):
				size = len(q)
		code["hirachy"][j] = size
		if(size == 0):
			zero_nodes.append(j)
		if(size > highest_level):
			highest_level = size

	code["max_level"] = highest_level

	if(len(zero_nodes) > 0):
		head = zero_nodes[0]
		found_non_zero = False
		for j in zero_nodes:
			if(j == head):
				continue
			size = 0
			for q in (dfs_path(code["edges"], head, j)):
				if(len(q) > size):
					size = len(q)
			#print("{}->{}".format(head, j))
			#print(size)
			code["hirachy"][j] = size
			if(size > 0):
				found_non_zero = True

	return code

if __name__ == "__main__":
	test_graphviz({"edges":{"0x4004b6":["0x4004a0"],"0x4004c6":["0x4004a0"],"0x4004d6":["0x4004a0"]},"type":{"0x4004b6":["jumpted"],"0x4004c6":["jumpted"],"0x4004d6":["jumpted"]},"code":{"0x4004a0":[{"address":"0x4004a0","instruction":"push","argument":"qword ptr [rip + 0x200b62]"},{"address":"0x4004a6","instruction":"jmp","argument":"qword ptr [rip + 0x200b64]"}],"0x4004ac":[{"address":"0x4004ac","instruction":"nop","argument":"dword ptr [rax]"},{"address":"0x4004b0","instruction":"jmp","argument":"qword ptr [rip + 0x200b62]"}],"0x4004b6":[{"address":"0x4004b6","instruction":"push","argument":"0"},{"address":"0x4004bb","instruction":"jmp","argument":"0x4004a0"}],"0x4004c0":[{"address":"0x4004c0","instruction":"jmp","argument":"qword ptr [rip + 0x200b5a]"}],"0x4004c6":[{"address":"0x4004c6","instruction":"push","argument":"1"},{"address":"0x4004cb","instruction":"jmp","argument":"0x4004a0"}],"0x4004d0":[{"address":"0x4004d0","instruction":"jmp","argument":"qword ptr [rip + 0x200b52]"}],"0x4004d6":[{"address":"0x4004d6","instruction":"push","argument":"2"},{"address":"0x4004db","instruction":"jmp","argument":"0x4004a0"}]},"flow":["0x4004b6","0x4004c6","0x4004d6"],"start":"0x4004a0","end":"0x4004db","hirachy":{"0x4004a0":1,"0x4004ac":0,"0x4004b6":0,"0x4004c0":0,"0x4004c6":0,"0x4004d0":0,"0x4004d6":0}})
#	pass



