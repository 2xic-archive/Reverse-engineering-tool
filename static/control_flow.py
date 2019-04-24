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
	def __init__(self, from_node, to_node):
		self.from_node = from_node
		self.to_node = to_node
 
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
						new_relations.append(relation(start, code_block[i]["argument"]))
					else:
						continue

				if("jne" in code_block[i]["instruction"] or "je" in code_block[i]["instruction"] ):
					new_relations.append(relation(start, code_block[i + 1]["address"]))
 				
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
						self.node_relation[str(node_relation)] = [source, target]
					 
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
			 
			#   overlap = (blockStart < start_blockEnd) and start_blockEnd < blockEnd 
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
		for j in self.node_relation:
			from_node = j.split("->")[0]
			 
			if(from_node in dfs_edges.keys()):
				continue
 
			dfs_edges[from_node] = []
 
			for i in self.node_relation:
				if(from_node in i.split("->")[0]):
					to_node = i.split("->")[1]
					dfs_edges[from_node].append(to_node)
 
		return dfs_edges
 
	def return_node_code(self):
		code_nodes = {
 
		}
		for block in self.blocks:
			code_nodes[hex(block.start)] = block.instructions # block.instruction_string.split("\n")
		return code_nodes

#	helps for debugging :=)
def test_graphviz(input_cfg):
	from graphviz import Digraph
	grapth = Digraph()
	print(input_cfg)
	for node_key, node_value in input_cfg["code"].items():
		code = ""
		for code_block in node_value:
#			print(node_value)
			code += "%s\t%s\t%s\n" % (code_block["address"], code_block["instruction"], code_block["argument"])
		grapth.node(node_key, label=code)

	for node_key, node_value in input_cfg["edges"].items():
		for edges in node_value:
			grapth.edge(node_key, edges)
	grapth.view()
	input("press enter") 

def make_cfg(code):
	#   based on some code from 
	 
	#   https://www.cs.rice.edu/~keith/pubs/TR02-399.pdf
	#   https://www.diericx.net/post/generating-avr-assembly-control-flow-graphs/
	 
	code_cfg = cfg(code)
	code_cfg.store_blocks()
	code_cfg.clean_blocks()
 
	dfs_edges = code_cfg.return_edge_map()
	codebase = code_cfg.return_node_code()
#	test_graphviz({"edges":dfs_edges, "code":codebase, "flow":sorted(list(dfs_edges.keys()))})
#	exit(0)
	return {"edges":dfs_edges, "code":codebase, "flow":sorted(list(dfs_edges.keys())), 
		"start":code_cfg.start_address, "end":code_cfg.end_address}


