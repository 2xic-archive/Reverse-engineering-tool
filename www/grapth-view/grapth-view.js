
var last_message = undefined;

var last_index = 0;
var target_section = ".init";

var look_up_table = {

};

var refrence_key_node = {

}


var block_list = {

}

var ligther = new highlighter(); 
var global_row_index = undefined;

function look_up_section(address){
	var i;
	for(i = 0; i < look_up_table[target_section].length; i++){
		if(parseInt(address, 16) < parseInt(look_up_table[target_section][i], 16)){
			break;
		}
	}
	return (i - 1);
}

function clear_grapth(){
	document.getElementById("grapth").innerHTML = "<canvas id=\"canvas\"></canvas>";
}

function setup_canvas(size_width, size_heigth){
	var canvas = document.getElementById("canvas");
	var ctx = canvas.getContext("2d");

	canvas.width = size_width;
	canvas.height = size_heigth;

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
	return msg["code"][key];
}

function create_blocks(msg){
	var section_keys = Object.keys(msg);
	for(var q = 0; q < section_keys.length; q++){
		var section = section_keys[q];
		for(var i = 0; i < Object.keys(msg[section]).length; i++){
			var nodes = Object.keys(msg[section][i]["code"]);
			var edges = Object.keys(msg[section][i]["edges"]);

			for(var j = 0; j < nodes.length; j++){
				var node = nodes[j];
				var target = document.getElementById("flat_view_row_" + node);
				if(target != undefined){
					target.setAttribute("block_start", "");			
					if(block_list[node] == undefined){
						block_list[node] = "loc_" + node;
					}
				}
			}

			for(var j = 0; j < edges.length; j++){
				var node = edges[j];
				var target = document.getElementById("flat_view_row_" + node);
				if(target != undefined){
					target.setAttribute("block_start", "");
					if(block_list[node] == undefined){
						block_list[node] = "loc_" + node;
					}
				}
			}
			if(!look_up_table.hasOwnProperty(section)){
				look_up_table[section] = [];
			}
			look_up_table[section].push(msg[section][i]["start"]);
		}
		if(target_section == undefined){
			target_section = section;
		}
	}
}


function dfs_create_positon(stack){
	var visited = [];
	var lowest_x = 0;
	var highest_x = 0;
	while(stack.length > 0){
		var new_node = stack.shift();
		if(visited.indexOf(new_node.unqiue_id) == -1){
			visited.push(new_node.unqiue_id);
		}else{
			continue;
		}
		new_node.position_edges();
		for(var i = 0; i < new_node.edges.length; i++){
			stack.push(new_node.edges[i]);
			new_node.edges[i].position_edges();

			if(new_node.edges[i].padding < lowest_x){
				lowest_x = new_node.edges[i].padding;
			}
			if(highest_x < new_node.edges[i].padding ){
				highest_x = new_node.edges[i].padding;
			}
			
		}
	}
	return [lowest_x,  highest_x];
}

function dfs_set_in_position(stack, coordinates, levels){
	var visited = [];
	var level_look_up = {

	};
	var max_heigth = 0;
	while(stack.length > 0){
		var new_node = stack.shift();
		var new_coordinates = coordinates.shift();
		var new_level = levels.shift();

		if(visited.indexOf(new_node.unqiue_id) == -1){
			visited.push(new_node.unqiue_id);
		}else{
			if(level_look_up[new_node.hirachy_level] < new_coordinates[1]){
				var hirachy_level = Object.keys(level_look_up).length;
				var continuity = true;

			//	new_node.debug("trying to find a new location ... ");

				if(0 <= (new_node.hirachy_level - 1) && (new_node.hirachy_level + 1) <= hirachy_level){
					var previous_level = level_look_up[new_node.hirachy_level - 1];
					var next_level = level_look_up[new_node.hirachy_level + 1];

					if(!((previous_level < new_coordinates[1]) && (new_coordinates[1] < next_level))){
						continuity = false;
					}
				//	new_node.debug("stage 2 ..");
				}else if(0 <= (new_node.hirachy_level - 1) && new_node.hirachy_level == new_node.max_level){
					console.log(hirachy_level);
					console.log(new_node.hirachy_level);
					var previous_level = level_look_up[new_node.hirachy_level - 1];
					if(!(previous_level < new_coordinates[1])){
						continuity = false;
					}
				//	new_node.debug("stage 1..");		
				}else{
					continuity = false;
				}
			//	new_node.debug(JSON.stringify(level_look_up));
			//	new_node.debug("sucess ? " + continuity)
				if(continuity){
					level_look_up[new_node.hirachy_level] = new_coordinates[1];	
					new_node.place(new_node.x, new_coordinates[1]);
					new_node.debug(JSON.stringify(level_look_up));

					if(max_heigth < (new_coordinates[1] + new_node.heigth)){
						max_heigth = new_coordinates[1] + new_node.heigth;
					}

				}
			}
			continue;
		}

		if(Object.keys(level_look_up).indexOf(new_node.hirachy_level) == -1){
			level_look_up[new_node.hirachy_level] = new_coordinates[1];
			new_node.place(new_coordinates[0], new_coordinates[1]);	

			if(max_heigth < (new_coordinates[1] + new_node.heigth)){
				max_heigth = new_coordinates[1] + new_node.heigth;
			}
		}

		new_node.element_reference.setAttribute("orginal_x", new_coordinates[0]);

		var edge_count = new_node.edges.length;
		for(var i = 0; i < edge_count; i++){
			stack.push(new_node.edges[i]);
			if(edge_count > 1){
				coordinates.push([new_coordinates[0] + new_node.edges[i].padding, 
					new_coordinates[1] + new_node.vertical_gap + new_node.highest_heigth]);
			}else{
				coordinates.push([new_coordinates[0] + new_node.edges[i].padding, 
					new_coordinates[1] + new_node.vertical_gap + new_node.heigth]);
			}
			levels.push(new_node.edges[i].hirachy_level);
		}		
	}
	return max_heigth;
}



function dfs_draw(stack, ctx, mapping){
	var visited = [];
	var drawn_lines = {

	}
	while(stack.length > 0){
		var new_node = stack.shift();
			
		if(visited.indexOf(new_node.unqiue_id) == -1){
			visited.push(new_node.unqiue_id);
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
				
			var x0 = new_node.node_left + (new_node.width) / 2;
			var y0 = new_node.node_top + new_node.heigth;

			var x1 = new_node.edges[i].node_left +  (new_node.edges[i].width) / 2;
			var y1 = new_node.edges[i].node_top;

			var color = "black";
			if(mapping[new_node.unqiue_id][i] == "followed"){
				color = "red";
			}else if(mapping[new_node.unqiue_id][i] == "jumpted"){
				color = "green";
			}

			if(new_node.direction[i] == 1){
				if(y0 < y1){
					new_node.connect_nodes(
						ctx,
						x0, y0, 
						x1, y1, 
						color);

				}else{
					y1 = new_node.node_top;
					x1 = new_node.node_left + (new_node.width) / 2;

					y0 = new_node.edges[i].node_top + (new_node.edges[i].heigth);
					x0 = new_node.edges[i].node_left +  (new_node.edges[i].width) / 2;
					new_node.connect_nodes(
						ctx,
						x0, y0, 
						x1, y1,
						color);
				}
			}else{
				//	backward ... 
				if(x0 > x1 && y0 < y1){
					new_node.connect_nodes_curve(
						ctx,
						x0, y0, 
						x1, y1,
						300,
						color
					);
				}else{
					new_node.connect_nodes_curve(
						ctx,
						x0, y0, 
						x1, y1,
						-300,
						color);
				}
			}
		}
		new_node.draw();
	}
}


function create_grapth(msg, index){
	if(index != undefined){
		last_message = msg;
		last_index = index;
		
		msg = msg[target_section][index];
	}

	clear_grapth();	
		
	var nodes = Object.keys(msg["code"]);	
	refrence_key_node = {

	}

	for(var j = 0; j < nodes.length; j++){
		var node = nodes[j];
		var target = document.getElementById("flat_view_row_" + node);
		if(target != undefined){
			target.setAttribute("block_start", "")
		}
		refrence_key_node[node] = new tree_node(get_code(msg, node), msg["hirachy"][node]);
		refrence_key_node[node].max_level = msg["max_level"];
	}
	
	var edges = Object.keys(msg["edges"]);
	for(var i = 0; i < edges.length; i++){
		var key = edges[i];
		var children = [];
		var children_val = [];			
		for(var j = 0; j < msg["edges"][key].length; j++){
			var edge_node = msg["edges"][key][j];
			children.push(refrence_key_node[edge_node]);
			children_val.push(edge_node);
			if(edge_node == key){
				refrence_key_node[key].enable_self_refrence();
			}
		}	

		var new_root_node = refrence_key_node[key]; 
		var low_children = undefined;
		for(var j = 0; j < children.length; j++){
			if(key < children_val[j]){
				new_root_node.add_edge(children[j], 1);
			}else{				
				new_root_node.add_edge(children[j], -1);	
			}
		}
	}

	var root_node = refrence_key_node[msg["start"]];
	var root_heigth = parseInt(msg["start"], 16);
	root_node.is_root = true;

	var results = dfs_create_positon([root_node]);
	var lowest_x = Math.abs(results[0]) ;

	var root_x = root_node.horizontal_gap + lowest_x;
	var root_y = root_node.heigth / 2 + document.getElementsByName("grapth-div")[0].getBoundingClientRect().top;

	var max_heigth = dfs_set_in_position([root_node], [[root_x, root_y ]], [root_node.hirachy_level]);
	var max_width = lowest_x + results[1]+ root_node.width * 2;

	dfs_draw([root_node], setup_canvas(max_width, max_heigth), msg["type"]);

	build();
}

function redraw(){
	if(last_message != undefined){
		create_grapth(last_message, last_index);
		document.getElementsByName("grapth-div")[0].scroll(0, 0);
	}
}

window.onresize = function(){
	redraw();
}


