


'''
Code for testing Reingold-Tilford Algorithm, based off this tutorial(best place I found that 
described the algoritm)
	https://rachel53461.wordpress.com/2014/04/20/algorithm-for-drawing-trees/
'''
import uuid
import os
import os, sys

path = "/".join(os.path.realpath(__file__).split("/")[:-2]) + "/"
sys.path.append(path)

from common.model  import *
from common.grapth  import *
from elf.elf_parser import *
import json
import time

def test_grapth():
	working_model = model(elf("./test_binaries/fibonacci"), None)

	while not working_model.done_decompile:
		time.sleep(1)

	grapth_layout = working_model.cfg[".text"]

	index = 1
	for index in range(len(grapth_layout.keys())):
		nodes = {

		}
		print(grapth_layout.keys())
		for j in grapth_layout[index]["code"].keys():
			nodes[j] = tree(name=j)
		defined_already = {

		}
		root_node = nodes[grapth_layout[index]["start"]]
		for key, childs in grapth_layout[index]["edges"].items():
			refrence = nodes[key]
			for child in childs:
				if not (defined_already.get(child, False)):
					refrence.add_children(nodes[child])
					nodes[child].parrent = refrence
					defined_already[child] = True
		
		grapth_refrence = grapth()
		grapth_refrence.caclulate_node_positions(root_node)
	assert(True)