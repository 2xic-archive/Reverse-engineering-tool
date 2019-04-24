var last_message = undefined;
var last_index = 0;
var target_section = undefined;
var look_up_table = {};

function look_up_section(address){
	var i;
	for(i = 0; i < look_up_table[target_section].length; i++){
		if(parseInt(address, 16) < parseInt(look_up_table[target_section][i], 16)){
//			return i;
			break;
		}
	}
	return (i - 1);
}

function clear_grapth(){
	document.getElementById("grapth").innerHTML = "<canvas id=\"canvas\"></canvas>";
}

function setup_canvas(){
	var canvas = document.getElementById("canvas");
	var ctx = canvas.getContext("2d");

	canvas.width = 1000;
	canvas.height = 2500;

	return ctx;
}



function get_canvas_position(){
	var offsets = document.getElementById("canvas").getBoundingClientRect();
	var scroll_offset = document.getElementsByName("grapth-div")[0];//.scrollTop

	var top = offsets.top + scroll_offset.scrollTop;
	var left = offsets.left;
	return [top, left];
}

function get_code(msg, key){
	return msg["code"][key];//.join("<br>");
}

function create_blocks(msg){
	var section_keys = Object.keys(msg);
	for(var q = 0; q < section_keys.length; q++){
		var section = section_keys[q];
		for(var i = 0; i < Object.keys(msg[section]).length; i++){
			var nodes = Object.keys(msg[section][i]["code"]);
			var edges = Object.keys(msg[section][i]["edges"]);
			//console.log(nodes);

			for(var j = 0; j < nodes.length; j++){
				var node = nodes[j];
				/*var edges = msg[section][i]["edges"][node];
				for(var y = 0; y < edges.length; y++){
					document.getElementById("flat_view_row_" + edges[y]).setAttribute("block_start", "");				
				}*/
				document.getElementById("flat_view_row_" + node).setAttribute("block_start", "");
			}
			for(var j = 0; j < edges.length; j++){
				var node = edges[j];
				/*var edges = msg[section][i]["edges"][node];
				for(var y = 0; y < edges.length; y++){
					document.getElementById("flat_view_row_" + edges[y]).setAttribute("block_start", "");				
				}*/
				document.getElementById("flat_view_row_" + node).setAttribute("block_start", "");
			}
			if(Object.keys(look_up_table).indexOf(section) == -1){
				look_up_table[section] = [];
			}
			look_up_table[section].push(msg[section][i]["start"]);
		}
		if(target_section == undefined){
			target_section = section;
		}
	}
}

function create_grapth(msg, index){
	last_message = msg;
	last_index = index;
	
	msg = msg[target_section][index];

	clear_grapth();	
	
	var ctx = setup_canvas();

	var canvas_position = get_canvas_position();
	var canvas_position_top = canvas_position[0];
	var canvas_position_left = canvas_position[1];

	
	var nodes = Object.keys(msg["edges"]);
	var refrence_key_node = {

	}


	for(var i = 0; i < nodes.length; i++){
		var node = nodes[i];
		//console.log(node);
//		console.log(document.getElementById("flat_view_row_" + node));
		document.getElementById("flat_view_row_" + node).setAttribute("block_start", "")
		//document.getElementById("row_" + node).style.background = "red";
		for(var j = 0; j < msg["edges"][node].length; j++){
			var edge_node = msg["edges"][node][j];
			document.getElementById("flat_view_row_" + edge_node).setAttribute("block_start", "");//.style.background = "red";

			if(Object.keys(refrence_key_node).indexOf(edge_node) == -1){
				refrence_key_node[edge_node] = new tree_node(get_code(msg, edge_node), [canvas_position_top, canvas_position_left]);
			}
		}
		refrence_key_node[node] = new tree_node(get_code(msg, node), [canvas_position_top, canvas_position_left]);
	}


	var root_node = undefined;
	var root_heigth = undefined;
	
	for(var i = 0; i < nodes.length; i++){
		var key = nodes[i];
		var children = [];
		var children_val = [];			
		for(var j = 0; j < msg["edges"][key].length; j++){
			var edge_node = msg["edges"][key][j];
			children.push(refrence_key_node[edge_node]);
			children_val.push(edge_node);
		}	

		var new_root_node = refrence_key_node[key]; 
		for(var q = 0; q < children.length; q++){
			if(key < children_val[q]){
				new_root_node.add_edge(children[q], 1);
			}else{
				new_root_node.add_edge(children[q], -1);	
			}
		}
		if(root_node == undefined || parseInt(root_heigth, 16) > parseInt(key, 16)){
			root_heigth = key;
			root_node = new_root_node;
		}
	}
	if(root_node == undefined){
		//	if there are no edges, there will be no root...
		var node = Object.keys(msg["code"])[0];
		root_node =  new tree_node(get_code(msg, node), [canvas_position_top, canvas_position_left]);
	}

	function dfs_create_positon(stack){
		var visited = [];
		while(stack.length > 0){
			var new_node = stack.shift();
			if(visited.indexOf(new_node.gethash) == -1){
				visited.push(new_node.gethash);
			}else{
				continue;
			}
			new_node.position_edges();
			for(var i = 0; i < new_node.edges.length; i++){
				stack.push(new_node.edges[i]);
				new_node.edges[i].position_edges();
			}
		}
	}


	function dfs_set_in_position(stack, coordinates){
		var visited = [];
		while(stack.length > 0){
			var new_node = stack.shift();
			var new_coordinates = coordinates.shift();

			if(visited.indexOf(new_node.gethash) == -1){
				visited.push(new_node.gethash);
			}else{
				continue;
			}
			new_node.place(new_coordinates[0], new_coordinates[1]);
			for(var i = 0; i < new_node.edges.length; i++){
				stack.push(new_node.edges[i]);

				if(new_node.edges[i].highest_node_heigth == 0){
					if(new_node.is_root){
						coordinates.push([new_coordinates[0]  + new_node.edges[i].padding, new_coordinates[1]  + new_node.vertical_gap + new_node.heigth + new_node.edges[i].highest_node_heigth]);
					}else{
						coordinates.push([new_coordinates[0]  + new_node.edges[i].padding, new_coordinates[1]  + new_node.vertical_gap + new_node.edges[i].heigth]);
					}
				}else{
					coordinates.push([new_coordinates[0]  + new_node.edges[i].padding, new_coordinates[1]  + new_node.vertical_gap + new_node.heigth + new_node.edges[i].highest_node_heigth]);
				}
			}		
		}
	}



	function dfs_draw(stack){
		var visited = [];
		var drawn_lines = {

		}
		var heigth = 0;
		while(stack.length > 0){
			var new_node = stack.shift();
			
			if(visited.indexOf(new_node.gethash) == -1){
				visited.push(new_node.gethash);
			}else{
				continue;
			}

			for(var i = 0; i < new_node.edges.length; i++){
				stack.push(new_node.edges[i]);
				var node_from = new_node.code_block[0]["address"];
				var node_to = new_node.edges[i].code_block[0]["address"];

				var connection = node_from + node_to;
				var reversed_connection = node_to + node_from;
				
				if(Object.keys(drawn_lines).indexOf(reversed_connection) != -1 || Object.keys(drawn_lines).indexOf(connection) != -1){
					continue;
				}

				var x0 = new_node.x;
				var y0 = new_node.y + new_node.node_half_top;

				var x1 = new_node.edges[i].x;
				var y1 = new_node.edges[i].y - new_node.edges[i].node_half_top;

				if(new_node.highest_node_heigth != 0){

					if(new_node.direction[i] == 1){
						if(y1 < y0){
							new_node.connect_nodes(								
								ctx,
								x1, new_node.edges[i].y + new_node.edges[i].node_half_top,
								x0, new_node.y - new_node.heigth);
						}else{
							new_node.connect_nodes(
								ctx,
								x0, y0 , 
								x1, y1);
						}
					}			
				}
				else{
					if(new_node.direction[i] == 1){
						new_node.connect_nodes(
							ctx,
							x0, y0, 
							x1, new_node.edges[i].y - new_node.edges[i].node_half_top);	
					}
				}
				if(heigth < new_node.node_top ){
					heigth = new_node.node_top;
				}
				if(heigth < new_node.edges[i].node_top){
					heigth = new_node.edges[i].node_top;
				}
			}
			new_node.draw();
		}
//		console.log(heigth);
//		document.getElementById("canvas").setAttribute("height", heigth);
//		document.getElementById("grapth").style.maxHeight = "100px";
	}
	root_node.is_root = true;

	dfs_create_positon([root_node]);
	dfs_set_in_position([root_node], [[root_node.horizontal_gap + (50 + root_node.largest_padding / 2)  , root_node.heigth / 2 + canvas_position_top ]]);
	dfs_draw([root_node]);


	var ligther = new highlighter(); 
	$("tr").click(function(e){
		if(this.getAttribute("type") == "flat"){
			var old_target = target_section;
			target_section = this.getAttribute("section");
			console.log(target_section);
			var section = look_up_section(this.getAttribute("name").replace("row_", ""));
			if(section != last_index || old_target != target_section){
				create_grapth(last_message, section);
				document.getElementsByName("grapth-div")[0].scroll(0, 0);
			}
		}
//		console.log(this.rowIndex);
		var last_target = this.rowIndex;
		var target = document.getElementsByName(this.getAttribute("name"));
		ligther.highligth(target);
	});

}

function recalculate(){
	if(last_message != undefined){
		create_grapth(last_message, last_index);
		document.getElementsByName("grapth-div")[0].scroll(0, 0);
	}
}

window.onresize = function(){
	recalculate();
}

