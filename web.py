
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


@app.route("/<path:path>")
def folder_path(path):
	return send_from_directory(static_file_dir, path)

@socketio.on("online")
def event_code(json, methods=["GET", "POST"]):
	global target
	target = model(elf(sys.argv[1]))
	json = target.decompile_text()
#	print(json)
	socketio.emit("code", json)

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

@socketio.on("hex")
def event_code(json_data, methods=["GET", "POST"]):
	socketio.emit("hex_response", {"data":target.hex})

@socketio.on("get control")
def event_code(json_data, methods=["GET", "POST"]):
	socketio.emit("control", target.get_cfg())

@app.after_request
def add_header(request):
	request.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	request.headers["Pragma"] = "no-cache"
	request.headers["Expires"] = "0"
	request.headers["Cache-Control"] = "public, max-age=0"
	return request

if __name__ == "__main__":
	if(len(sys.argv) > 1):
		target = model(elf(sys.argv[1]))
		socketio.run(app, debug=True)
	else:
		print("scripy.py elf-binary")


