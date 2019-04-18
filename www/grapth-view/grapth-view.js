var last_message = undefined;

function clear_grapth(){
	document.getElementById("grapth").innerHTML = '<canvas id="canvas"></canvas>';
}

function setup_canvas(){
	var canvas = document.getElementById("canvas");
	var ctx = canvas.getContext("2d");

	canvas.width = 1000;
	canvas.height = 2000;

	return ctx;
}

function get_canvas_position(){
	var offsets = document.getElementById("grapth").getBoundingClientRect();
	var top = offsets.top;
	var left = offsets.left;
	return [top, left];
}

function get_code(msg, key){
	return msg["code"][key].join("<br>");
}

function create_grapth(msg){
	last_message = msg;
	
	clear_grapth();	
	
	var ctx = setup_canvas();

	var canvas_position = get_canvas_position();
	var canvas_position_top = canvas_position[0];
	var canvas_position_left = canvas_position[1];

	
	console.log(msg);

	var nodes = Object.keys(msg["edges"]);
	var refrence_key_node = {

	}


	for(var i = 0; i < nodes.length; i++){
		var node = nodes[i];
		for(var j = 0; j < msg["edges"][node].length; j++){
			var edge_node = msg["edges"][node][j];
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
					coordinates.push([new_coordinates[0]  + new_node.edges[i].padding, new_coordinates[1]  + new_node.vertical_gap + new_node.edges[i].heigth]);
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
		while(stack.length > 0){
			var new_node = stack.shift();
			
			if(visited.indexOf(new_node.gethash) == -1){
				visited.push(new_node.gethash);
			}else{
				continue;
			}

			for(var i = 0; i < new_node.edges.length; i++){
				stack.push(new_node.edges[i]);
				var node_from = new_node.content.split("<br>")[0].split("\t")[0];
				var node_to = new_node.edges[i].content.split("<br>")[0].split("\t")[0];

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
			}
			new_node.draw();
		}
	}
	console.log(msg);
	dfs_create_positon([root_node]);
	dfs_set_in_position([root_node], [[root_node.horizontal_gap + (50 + root_node.largest_padding / 2)  , root_node.heigth / 2 + canvas_position_top]]);
	dfs_draw([root_node]);	
	root_node.element_refrence.style.background = 'red';

}

function recalculate(){
	if(last_message != undefined){
		create_grapth(last_message);
	}
}

window.onresize = function(){
	recalculate();
}

