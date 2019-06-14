


'''
Code for testing Reingold-Tilford Algorithm, based off this tutorial(best place I found that 
described the algoritm)
	https://rachel53461.wordpress.com/2014/04/20/algorithm-for-drawing-trees/
'''

import uuid
from flask import send_from_directory
import os
from flask_socketio import SocketIO
from flask import Flask, render_template
from flask_socketio import SocketIO

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from model import *
from grapth import *


if __name__ == "__main__":
	working_model = model(elf("../../test_binaries/fibonacci"), None)
	import json
#	print(json.dumps(list(working_model.decompiled_sections.values())[0]))
#	print()
#	exit(0)
#	grapth_layout = json.dumps(list(working_model.cfg.values())[0])	
#	print(grapth_layout)
#	exit(0)

#	print(working_model.cfg.keys())
#	print(list(working_model.cfg.values())[0])
#	exit(0)
	grapth_layout = working_model.cfg[".text"]#list(working_model.cfg.values())[0]


	exit(0)

	index = 1
	for index in range(len(grapth_layout.keys())):
	#if(True):
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
		print(grapth_refrence.grapth_layout)

	