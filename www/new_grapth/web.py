


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

app = Flask(__name__)
app.config["SECRET_KEY"] = b'u\xe6\xd6\x80\xda 5C\xeb\xa2\xec\xb5\x1fx\xf4J|\xe1\xa0\xb8n\xc3^\x9c'

socketio = SocketIO(app)

target = None
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "") + "/"


@app.route("/")
def sessions():
	return send_from_directory(static_file_dir, "new_grapth_view.html")
'''
grapth_layout = {"0": 
							{"edges": 
								{"0x400480": ["0x400492", "0x400490"], 
								"0x400490": ["0x400492"]}, 
							"type": 
								{"0x400480": ["jumpted", "followed"], 
								"0x400490": ["0x400492"]}, 
							"code": {"0x400480": 
								[{"address": "0x400480", "instruction": "sub", "argument": "rsp, 8"}, 
								{"address": "0x400484", "instruction": "mov", "argument": "rax, qword ptr [rip + 0x200b6d]"}, {"address": "0x40048b", "instruction": "test", "argument": "rax, rax"}, {"address": "0x40048e", "instruction": "je", "argument": "0x400492"}], "0x400492": [{"address": "0x400492", "instruction": "add", "argument": "rsp, 8"}, {"address": "0x400496", "instruction": "ret", "argument": ""}], "0x400490": [{"address": "0x400490", "instruction": "call", "argument": "rax"}]}, "flow": ["0x400480", "0x400490"], "start": "0x400480", "end": "0x400496", 
							"hirachy": {"0x400480": 1, "0x400492": 3, "0x400490": 2}, "max_level": 3}}
'''

@socketio.on("online")
def event_code(methods=["GET", "POST"]):
	global grapth_layout
	socketio.emit("draw",{ 
				"layout":grapth_refrence.grapth_layout,
				"code":grapth_layout["0"]["code"],
				"edges":grapth_layout["0"]["edges"]
			}
	)

if __name__ == "__main__":
	working_model = model(elf("../../test_binaries/fibonacci"), socketio)
	import json
#	print(json.dumps(list(working_model.decompiled_sections.values())[0]))
#	print()
#	exit(0)
#	grapth_layout = json.dumps(list(working_model.cfg.values())[0])	
#	print(grapth_layout)
#	exit(0)

	grapth_layout = list(working_model.cfg.values())[0]

	nodes = {

	}
	print(grapth_layout.keys())
	for j in grapth_layout[0]["code"].keys():
		nodes[j] = tree(name=j)

	root_node = nodes[grapth_layout[0]["start"]]
	for key, childs in grapth_layout[0]["edges"].items():
		refrence = nodes[key]
		for child in childs:
		#	defined_already[child] = False 
			refrence.add_children(nodes[child])
			nodes[child].parrent = refrence
	
	grapth_refrence = grapth()
	grapth_refrence.caclulate_node_positions(root_node)
	print(grapth_refrence.grapth_layout)

	exit(0)

	'''
	grapth_layout = {"0": 
					{"edges": {"0x400480": ["0x400492", "0x400490"], "0x400490": ["0x400492"]}, 
					"type": {"0x400480": ["jumpted", "followed"], "0x400490": ["0x400492"]}, 
					"code": {"0x400492": "0x400496", "0x400490": "0x400490", "0x400480": "0x40048e"}, "start": "0x400480"}}

#	print(grapth_layout["0"]["code"].keys())
	nodes = {

	}
	for j in grapth_layout["0"]["code"].keys():
		nodes[j] = tree(name=j)

	root_node = nodes[grapth_layout["0"]["start"]]
	for key, childs in grapth_layout["0"]["edges"].items():
		refrence = nodes[key]
		for child in childs:
		#	defined_already[child] = False 
			refrence.add_children(nodes[child])
			nodes[child].parrent = refrence
	'''
	grapth_refrence = grapth()
	grapth_refrence.caclulate_node_positions(root_node)
	socketio.run(app, debug=True, host= '0.0.0.0')#, port=81)

	print((root_node.x, root_node.y))
	print((root_node.children[0].x, root_node.children[0].y))
	print((root_node.children[1].x, root_node.children[1].y))





