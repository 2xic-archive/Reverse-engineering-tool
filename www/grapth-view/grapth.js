
var ligther = new highlighter(); 

var last_message = undefined;

var refrence_key_node = {

}

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
	table.setAttribute("name", "graph_table_code");
	
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

function draw(msg){
	last_message = msg;
	boundary = msg["boundary"];

	var grapth = msg["layout"];
	var code_hint = msg["code"];

	var padding_top = 100;
	var padding_left = 100;
	var space_between_nodes = 50;

	var nodes = Object.keys(grapth);

	//	you process one level
	//	then you check the highest node, that node will have the y of next level + padding

	var section_name = msg["section_name"];

	console.log(code_hint);
	var last_heigth_max = 0;
	var last_width_max = 0;

	var canvas_heigth = 0;
	var canvas_width = 0;
	for (var level = 0; level < nodes.length; level++) {
	    var max = 0;
	    for (var node = 0; node < grapth[level].length; node++) {
	        if (0 <= grapth[level][node][0].indexOf("hidden")) {
	            continue;
	        }
	        var drawn = create_node(padding_left + grapth[level][node][1], padding_top + last_heigth_max + grapth[level][node][2], grapth[level][node][0], code_hint[grapth[level][node][0]],
	            section_name);

	        var drawn_element = drawn[0];
	        drawn_element.setAttribute("id", grapth[level][node][0]);

	        canvas_width = Math.max(drawn[1], canvas_width);
	        canvas_heigth = Math.max(drawn[2], canvas_heigth);

	        var offsetHeight = drawn_element.offsetHeight;
	        var offsetWidth = drawn_element.offsetWidth;

	        max = Math.max(max, offsetHeight);

	        last_width_max = Math.max(last_width_max, padding_left + grapth[level][node][1]);
	    }
	    last_heigth_max += (max + space_between_nodes);
	}

	var edges = msg["edges"];
	var head_edges = Object.keys(edges);


	//	0x4006ce
	//	300 is node
	var ctx = setup_canvas(canvas_width + 300, canvas_heigth + 300);
//	console.log([last_heigth_max, last_width_max, canvas_heigth])

	var delta = document.getElementsByName("grapth-div")[0].getBoundingClientRect();




	for (var i = 0; i < head_edges.length; i++) {
	    var working_head = head_edges[i];
	    console.log(working_head);

	    var head = document.getElementById(working_head);

	    if (head == null) {
	        //	console.log("why null ? " + working_head);
	        continue;
	    }


	    var xy = head.getBoundingClientRect();

	    //	-	5 is for the border size
	    var x0 = (xy.left + (xy.width) / 2) - delta.left;
	    var y0 = (xy.top + xy.height) - delta.top;


	    refrence_key_node[working_head] = [];


	    for (var j = 0; j < edges[working_head].length; j++) {
	        var edge_id = edges[working_head][j];
	        var edge = document.getElementById(edge_id);
	        if (edge == null) {
	            //			console.log("why null ? " + edge_id);
	            continue;
	        }

	        refrence_key_node[working_head].push(edge);

	        var edge_xy = edge.getBoundingClientRect();
	        var x1 = (edge_xy.left + (edge_xy.width) / 2) - delta.left;
	        var y1 = (edge_xy.top) - delta.top;

	        ctx.beginPath();
	        ctx.strokeStyle = "red";
	        ctx.moveTo(x0, y0);

	        if (x0 == x1) {
	            ctx.quadraticCurveTo(x0, y0, x1, y1);
	        } else if (x0 < x1) {
	            ctx.quadraticCurveTo(x0 + 50, y0, x1, y1);
	        } else {
	            ctx.quadraticCurveTo(x0 - 50, y0, x1, y1);
	        }
	        ctx.stroke();
	    }
	}
}


function redraw(){
	if(last_message != undefined){
		//create_grapth(last_message, last_index);
		draw(last_message);
//		document.getElementsByName("grapth-div")[0].scroll(0, 0);
	}
}

window.onresize = function(){
	redraw();
}


