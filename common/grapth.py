class tree:
	def __init__(self, parrent=None, name=None):
		self.x = 0
		self.y = 0

		self.width = 0
		self.heigth = 0

		self.heigth = 1

		self.mod = 0
		self.parrent = parrent
		self.children = []

		if not self.parrent == None:
			self.parrent.add_children(self)

		if(name == None):
			self.name = uuid.uuid4().hex
		else:
			self.name = name

	def node_id(self):
		return self.name

	def add_children(self, node):
		self.children.append(node)
		node.heigth = self.heigth + 1

	def get_children_heigth(self):
		return self.heigth + 1

	def add_if_unique(self, node):
		if node not in self.children:
			self.children.append(node)

	def is_leaf(self):
		return len(self.children) == 0

	def is_left_most(self):
		if(self.parrent == None):
			return True

		return self.parrent.children[0] == self

	def is_rigth_most(self):
		if(self.parrent == None):
			return True

		return self.parrent.children[-1] == self
	

	def get_previous_sibling(self):
		if(self.parrent == None or self.is_left_most()):
			return None

		return self.parrent.children[self.parrent.children.index(self) - 1]

	def get_next_sibling(self):
		if(self.parrent == None or self.is_rigth_most()):
			return None

		return self.parrent.children[self.parrent.children.index(self) + 1]

	def get_left_most_sibling(self):
		if(self.parrent == None):
			return None

		if(self.is_left_most()):
			return self	

		return self.parrent.children[0]

	def get_left_most_child(self):
		if(len(self.children) == 0):
			return None
		
		return self.children[0]

	def get_rigth_most_child(self):
		if(len(self.children) == 0):
			return None

		return self.children[-1]

class grapth:
	def __init__(self):
		self.node_size = 300
		self.sibling_distance = 250
		self.tree_distance = 10#100.0

		self.grapth_layout = {

		}

	def caclulate_node_positions(self, root):
		self.initalize(root, 0)
		self.calculate_initali_x(root)
		self.check_all_children_on_screen(root)
		self.calculate_final_position(root, 0)

	def initalize(self, node, depth):
		node.x = -1
		node.y = depth

		for child in node.children:
			self.initalize(child, depth + 1)

	def calculate_final_position(self, node, mod_sum):
		node.x += mod_sum
		mod_sum += node.mod

		for child in node.children:
			self.calculate_final_position(child, mod_sum)

		if(len(node.children) == 0):
			node.width = node.x
			node.heigth = node.y
		else:
			smallest_width = []
			smallest_heigth = []
			for child in node.children:
				smallest_width.append(child.width)
				smallest_heigth.append(child.heigth)
			node.width = min(smallest_width)
			node.heigth = max(smallest_heigth)

		if(self.grapth_layout.get(node.y, None) == None):
			self.grapth_layout[node.y] = []
		self.grapth_layout[node.y].append([node.node_id(), node.x, node.y])

	def calculate_initali_x(self, node):
		
		for child in node.children:
			self.calculate_initali_x(child)

		if(node.is_leaf()):
			if not node.is_left_most():
				node.x = node.get_previous_sibling().x + self.node_size + self.sibling_distance
			else:
				node.x = 0
		elif(len(node.children) == 1):
			if(node.is_left_most()):
				node.x = node.children[0].x
			else:
				node.x = node.get_previous_sibling().x + self.node_size + self.sibling_distance
		else:
			left = node.get_left_most_child()
			rigth = node.get_rigth_most_child()
			middle = (left.x + rigth.x) / 2

			if(node.is_left_most()):
				node.x = middle
			else:
				node.x = node.get_previous_sibling().x + self.node_size + self.sibling_distance
				node.mod = node.x - middle

		if(len(node.children) > 0 and not node.is_left_most()):
			self.check_for_conflics(node)

	def check_for_conflics(self, node):
		minimum_distance = self.tree_distance + self.node_size
		value_shift = 0

		node_counter = {

		}
		self.get_left_counter(node, 0, node_counter)

		sibling = node.get_left_most_sibling()
		while(sibling != None and sibling != node):
			sibling_counter = {

			}
			self.get_rigth_counter(sibling, 0, sibling_counter)
			level = node.y + 1
			while(level < min(min(sibling_counter.keys()), min(node_counter.keys()))):
				distance = node_counter[level] - sibling_counter[level]
				if((distance + value_shift) < minimum_distance):
					value_shift = minimum_distance - distance
				level += 1

			if(0 < value_shift):
				node.x += value_shift
				node.mod += value_shift
				self.center_node_between(node, sibling)
				value_shift = 0
			sibling = sibling.get_next_sibling()
			#for level in range(node.y + 1, )

	def center_node_between(self, left, rigth):
		left_index = left.parrent.children.index(rigth)
		rigth_index = left.parrent.children.index(left)

		nodes_between = (rigth_index - left_index) - 1

		if(0 < nodes_between):
			distance_between = (left.x - rigth.x)/(nodes_between + 1)
			count = 1
			for i in range(left_index + 1, rigth_index):
				middle_node = left.parrent.children[i]

				desired_x = rigth.x + (distance_between * count)
				offset = desired_x - middle_node.x

				middle_node.x += offset
				middle_node.mod += offset

				count += 1
			self.check_for_conflics(left)


	def check_all_children_on_screen(self, node):
		node_counter = {

		}
		self.get_left_counter(node, 0, node_counter)

		value_shift = 0
		for y in node_counter.keys():
			if(node_counter[y] + value_shift < 0):
				value_shift = (node_counter[y] * -1)

		if(0 < value_shift):
			node.x += value_shift
			node.mod += value_shift

	def get_left_counter(self, node, mod_sum, dicionary_refrence):
		if(dicionary_refrence.get(node.y, None) == None):
			dicionary_refrence[node.y] = (node.x + mod_sum)
		else:
			dicionary_refrence[node.y] = min(dicionary_refrence[node.y], node.x + mod_sum)

		mod_sum += node.mod

		for child in node.children:
			self.get_left_counter(child, mod_sum, dicionary_refrence)

	def get_rigth_counter(self, node, mod_sum, dicionary_refrence):
		if(dicionary_refrence.get(node.y, None) == None):
			dicionary_refrence[node.y] = (node.x + mod_sum)
		else:
			dicionary_refrence[node.y] = max(dicionary_refrence[node.y], node.x + mod_sum)

		mod_sum += node.mod

		for child in node.children:
			self.get_rigth_counter(child, mod_sum, dicionary_refrence)

def get_grapth_layout(grapth_layout):
	nodes = {

	}
	nodes["hidden_node"] = tree(name="hidden")
	for j in grapth_layout["code"].keys():
		nodes[j] = tree(name=j)

	'''
		need a better way to solve heigth conflics....
			can have it be using a stack instead of recursion,
			don't revist already visited nodes...
	'''
	root_node = nodes["hidden_node"]
	for key, childs in grapth_layout["edges"].items():
		refrence = nodes[key]
		for child in childs:
			if(nodes[child].parrent == None):
				refrence.add_children(nodes[child])
				nodes[child].parrent = refrence
			elif(nodes[child].heigth < refrence.get_children_heigth()):
				old_parrent = nodes[child].parrent
				old_parrent_child_index = old_parrent.children.index(nodes[child])
				old_parrent.children[old_parrent_child_index] = tree(name="hidden")

				refrence.add_children(nodes[child])
				nodes[child].parrent = refrence

	root_node.add_if_unique(nodes[grapth_layout["start"]])

	grapth_refrence = grapth()
	grapth_refrence.caclulate_node_positions(root_node)

	return grapth_refrence.grapth_layout


