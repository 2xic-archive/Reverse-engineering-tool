import hashlib
from collections import OrderedDict

class block:
	def __init__(self):
		self.instructions = []
		self.instruction_string = ""
		self.start = None
		self.end = None
 
	def add(self, instruction):
		if(self.start == None):
			self.start = instruction["address"]#.replace("0x", ""), 16)
		
		from copy import deepcopy

		new_in = deepcopy(instruction)
		new_in["address"] = hex(new_in["address"])


		self.instructions.append(new_in)

		self.instruction_string += hex(instruction["address"]) + "\t" + instruction["instruction"] + instruction["argument"] + "\n"
		self.end =  instruction["address"]#.replace("0x", ""), 16)
 
	def reconstruct(self):
		self.instruction_string = ""
		for instruction in self.instructions:
			self.instruction_string += instruction["address"] + "\t" + instruction["instruction"] + instruction["argument"] + "\n"
 
	def __str__(self):
		hash_object = hashlib.md5(self.instruction_string.encode())
		return hash_object.hexdigest()

	def __hash__(self):
	#	hash_object = hashlib.md5(self.instruction_string.encode())
	#	return hash_object.hexdigest()
		return hash(self.get_hasb())

	def get_hasb(self):
		hash_object = hashlib.md5(self.instruction_string.encode())
		return hash_object.hexdigest()
	
	def __eq__(self, other):
		return self.get_hasb() == other.get_hasb() 

class relation:
	def __init__(self, from_node, to_node, relation_type=None):
		self.from_node = from_node
		self.to_node = to_node
		self.type = relation_type
 
	def __str__(self):
		return hex(self.from_node) + "->" + hex(self.to_node)
 
class cfg:
	def __init__(self, code):
		self.node_relation = OrderedDict()
		self.visited_node = OrderedDict()
		self.instruction = code
		#self.start_address = code[0]["address"]
		self.start_address = self.instruction[0]["address"]
		self.end_address = self.instruction[-1]["address"]
		self.blocks = set()
		self.call_stack = []
 
	def in_scope(self, address):
		if(address[0].isalpha()):
			return False
		address = int(address, 16)

		return self.start_address <= address <= self.end_address

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

				if("jne" in code_block[i]["instruction"] or "je" in code_block[i]["instruction"] or "jmp" in code_block[i]["instruction"] ):
					if(self.in_scope(code_block[i]["argument"])):
						new_relations.append(relation(start, int(code_block[i]["argument"],16) , "jumpted"))

				if("jne" in code_block[i]["instruction"] or "je" in code_block[i]["instruction"] ):
					new_relations.append(relation(start, code_block[i + 1]["address"], "followed"))
 				
				yield new_block
 
				for node_relation in new_relations:
					source = node_relation.from_node
					target = node_relation.to_node
 
					if not str(node_relation) in self.node_relation.keys():
						self.node_relation[str(node_relation)] = [hex(source), hex(target), node_relation.type]
					 
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

				if(blockEnd == start_blockEnd and start_blockStart !=blockStart):
					biggest_block = other_blocks if(blockStart > start_blockStart) else blocks
					small = blocks if(blockStart > start_blockStart) else other_blocks
 
					pop_instructions = []
					for i in range(len(biggest_block.instructions)):
						instruction = biggest_block.instructions[i]
						if(int(instruction["address"], 16) >= small.start):
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
							new_relation = relation(biggest_block.start, int(val[1], 16))
							self.node_relation[str(new_relation)] = [hex(biggest_block.start), (val[1])]
 
							relations_to_remove.append(key)             
 
					for node_relation in relations_to_remove:
						self.node_relation.pop(node_relation)
				
					new_relation = relation(biggest_block.start, small.start)
					self.node_relation[str(new_relation)] = [hex(biggest_block.start), hex(small.start)]
				else:
					continue
 
 
	def store_blocks(self, target=None, count=0):
		for blocks in self.parse_code_block(target):
			self.blocks.add(blocks)
		
		found_all = False
		highest_address = None
		for j in self.blocks:
			if(j.end == self.end_address):#, 16)):
				found_all = True
				break
			if(highest_address == None or highest_address < j.end):
				highest_address = j.end

		'''
			hm... strange
		'''
		if not found_all:
			block = self.get_block(hex(highest_address))
			if(len(block) > 1):
				real_highest = block[1]["address"]
				return self.store_blocks(real_highest, count=count + 1)
 
	def return_edge_map(self):
		dfs_edges = OrderedDict()
		edge_type = OrderedDict()

		for relations_from in self.node_relation:
			from_node = relations_from.split("->")[0]
			 
			if(from_node in dfs_edges.keys()):
				continue
 
			dfs_edges[from_node] = []
			edge_type[from_node] = []

			for relations_to in self.node_relation:
				if(from_node in relations_to.split("->")[0]):
					to_node = relations_to.split("->")[1]
					dfs_edges[from_node].append(to_node)
					edge_type[from_node].append(self.node_relation[relations_to][- 1])

		return dfs_edges, edge_type
 
	def return_node_code(self):
		code_nodes = OrderedDict()
		for block in self.blocks:

			if(True):
				code_nodes[hex(block.start)] = block.instructions[-1]["address"]
			else:
				code_nodes[hex(block.start)] = block.instructions

		return code_nodes


	def dfs_path(self, grapth, start, end):
		stack = [(start, [start])]
		visited_node = []
		while len(stack) > 0:
			(vertex, current_path) = stack.pop()
			if(vertex in grapth.keys() and vertex not in visited_node):
				for edges in (set(grapth[vertex]) - set(current_path)):
					if(edges == end):
						yield current_path + [edges]
					else:
						stack.append((edges, current_path + [edges]))
				visited_node.append(vertex)

	def hirachy(self):
		dfs_edges, dfs_edges_type = self.return_edge_map()
		grapth = {
			"edges":dfs_edges,
			"type":dfs_edges_type,
			"code":self.return_node_code(),
			"flow":sorted(list(dfs_edges.keys())),
			"start":hex(self.start_address)	, 
			"end":hex(self.end_address)
		}
		'''
		head = grapth["start"]
		grapth["hirachy"] = OrderedDict()
		grapth["hirachy"][head] = 1
		zero_nodes = []

		highest_level = 0

#		print("code blocks %i" % (len(grapth["code"].keys())))
		for code_block in grapth["code"].keys():
			if(code_block == head):
				continue

			length = 0
			for valid_paths in self.dfs_path(grapth["edges"], head, code_block):
				if(len(valid_paths) > length):
					length = len(valid_paths)
			
			grapth["hirachy"][code_block] = length
			if(length == 0):
				zero_nodes.append(code_block)

			if(length > highest_level):
				highest_level = length

		grapth["max_level"] = highest_level
		assert (len(zero_nodes) == 0), "Found a zero node, implement a handler"
		'''
		return grapth


#	helps for debugging :=)
def test_graphviz(input_cfg):
	from graphviz import Digraph	
	grapth = Digraph()
	print(input_cfg)
	for node_key, node_value in input_cfg["code"].items():
		code = ""
		for code_block in node_value:
			code += "%s\t%s\t%s\n" % (code_block["address"], code_block["instruction"], code_block["argument"])
		grapth.node(node_key, label=code)
	
	for node_key, node_value in input_cfg["edges"].items():
		for edges in node_value:
			grapth.edge(node_key, edges)
			print("{}->{}".format(node_key, edges))
	grapth.view()
	exit(0)

def make_cfg(code):
	#   based on some code from 
	 
	#   https://www.cs.rice.edu/~keith/pubs/TR02-399.pdf
	#   https://www.diericx.net/post/generating-avr-assembly-control-flow-graphs/


	#print(code)
	code_cfg = cfg(code)
	code_cfg.store_blocks()
	code_cfg.clean_blocks() 
	return code_cfg.hirachy()


