
from flask import send_from_directory
import os
from flask_socketio import SocketIO
from elf.elf_parser import *
from flask import Flask, render_template
from flask_socketio import SocketIO
from static.assembler import *
from model import *

app = Flask(__name__)
app.config["SECRET_KEY"] = b'u\xe6\xd6\x80\xda 5C\xeb\xa2\xec\xb5\x1fx\xf4J|\xe1\xa0\xb8n\xc3^\x9c'


socketio = SocketIO(app)

target = None
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "www") + "/"


@app.route("/")
def sessions():
	return send_from_directory(static_file_dir, "index.html")

'''
@app.route("/block")
def check_block():
	import json
	global target
	open("big_binary.txt", "w").write( json.dumps({"code":target.decompiled_sections,
		 "sections":target.static.section_sizes,
		 "grapth":target.cfg,
		 "hex":target.hex
	}))
	return "dumped"

	json.dumps({"code":target.decompiled_sections,
		 "sections":target.static.section_sizes,
		 "grapth":target.cfg
		})
'''
#	return json.loads(open("big_binary.txt", "r").read())

@socketio.on("test_compress_server")
def check_block():
	print("got it")
	import json
	import base64
	import zlib  
	import binascii
	data = open("big_binary.txt", "r").read().encode() #open("big_binary.txt", "r").read().encode()

	compress = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, +15)  
	compressed_data = compress.compress(data)  
	compressed_data += compress.flush()

#	print(str(base64.b64encode(compressed_data)))
	print("yo")
	socketio.emit("test_compress", (base64.b64encode(compressed_data)).decode())	

@app.route("/<path:path>")
def folder_path(path):
	return send_from_directory(static_file_dir, path)

@socketio.on("online")
def event_code(methods=["GET", "POST"]):
	global target
	print("sending the binary data")
	socketio.emit("block", 
		{"code":target.decompiled_sections,
		 "sections":target.static.section_sizes,
		 "grapth":target.cfg
		}
	)
	socketio.emit("hex_response", {"data":target.hex})


@socketio.on("assemble instruction")
def event_code(json_data, methods=["GET", "POST"]):
	import json
	socketio.emit("error", "disabled")	
	'''
	assembly = ";".join(json_data["data"][1:])
	target_section = json_data["data"][0]
	new_byte_section = []
	try:
		assembled_instruction = assemble(assembly)
		new_byte_section.extend(assembled_instruction)
	except Exception as e:
		socketio.emit('error', '{}	=	{}'.format(assembly, e))	
	target.reconstruct_small(target_section, new_byte_section)
	'''

@socketio.on("get instruciton size")
def event_code(json_data, methods=["GET", "POST"]):
	socketio.emit("size response", {"size":len(assemble(json_data["data"][0])), "target":json_data["data"][1]})

@socketio.on("get control")
def event_code(json_data, methods=["GET", "POST"]):
	socketio.emit("control", target.get_cfg())


@socketio.on("give_grapth")
def event_code(methods=["GET", "POST"]):
	global target
	working_model = target
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
	socketio.emit("draw",{ 
				"layout":grapth_refrence.grapth_layout,
				"code":grapth_layout[0]["code"],
				"edges":grapth_layout[0]["edges"]
			}
	)



@socketio.on("dynamic_info")
def event_code(json_data, methods=["GET", "POST"]):
#	socketio.emit("control", target.get_cfg())
#	print("we out here ... ")
#	print(json_data["data"]["address"])
	socketio.emit("dynamic_data", target.dynamic.get_register_data(json_data["data"]["address"]))


@socketio.on("comments")
def event_code(json_data, methods=["GET", "POST"]):
	content = json_data["data"]
	target.add_comment(content[0], content[1])
	target.save_comment()

@socketio.on("save")
def event_code(json_data, methods=["GET", "POST"]):
#	print(json_data)
	print(json_data)
	target.save_model(json_data["data"]["file_name"])
#	content = json_data["data"]
#	target.add_comment(content[0], content[1])
#	target.save_comment()
	#print(target.custom_comments)
	#socketio.emit("control", target.get_cfg())

@socketio.on("give_me_dynamic_data")
def event_code(methods=["GET", "POST"]):
#	print("im happy")
	socketio.emit('dynamic_view', {"data":target.dynamic.address_register})

#	print(json_data)
#	print(json_data)
#	target.save_model(json_data["data"]["file_name"])



@app.after_request
def add_header(request):
	request.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	request.headers["Pragma"] = "no-cache"
	request.headers["Expires"] = "0"
	request.headers["Cache-Control"] = "public, max-age=0"
	return request


def exit_handler():
	# auto save ? 
	pass


if __name__ == "__main__":
	if(len(sys.argv) > 1):
		import atexit
		atexit.register(exit_handler)
		if(sys.argv[1].endswith(".pickle")):
			pikcle_data = open(sys.argv[1], "rb") 
			target = pickle.load(pikcle_data)
		else:
			target = model(elf(sys.argv[1]), socketio)
		socketio.run(app, debug=True, host= '0.0.0.0', port=81)
	else:
		print("scripy.py elf-binary")



