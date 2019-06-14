
function clear_canvas() {
	document.getElementById("grapth").innerHTML = "<canvas id=\"canvas\"></canvas>";
}

function setup_canvas(size_width, size_heigth) {
	var canvas = document.getElementById("canvas");
	var ctx = canvas.getContext("2d");

	document.getElementById("container_item_70").scrollTop = 0;
	document.getElementById("container_item_70").scrollLeft = 0;
	
	canvas.width = size_width;
	canvas.height = size_heigth;

	return ctx;
}


function create_node(x, y, start, finish, section_name) {
	var level_node = document.createElement("div");

	level_node.setAttribute("class", "node");

	level_node.style.left = x + "px";
	level_node.style.top = y + "px";

	code = code_lookup[section_name];

	var table = document.createElement("table");
	var addresses = Object.keys(code["code"]);

	table.setAttribute("tabindex", "0");
	table.setAttribute("name", "grapth_table_code");
	
	for (var i = (addresses.indexOf(start)); i <= addresses.indexOf(finish); i++) {
		var tr = document.createElement("tr");

//		console.log(i);
//		console.log(addresses[i]);
//		console.log(code["code"]);

		var code_data = code["code"][addresses[i]];
//		console.log(code_data);

		var address = document.createElement("td");
		address.innerText = addresses[i];

		var code_element = document.createElement("td");
		code_element.innerText = code_data["instruction"] + "\t" + code_data["argument"];


		tr.setAttribute("name", addresses[i]);
		tr.appendChild(address);
		tr.appendChild(code_element);
		table.appendChild(tr);
	}

	level_node.appendChild(table);

	document.getElementById("grapth").appendChild(level_node);
	return [level_node, x, y];
}





