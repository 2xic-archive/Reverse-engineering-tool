

var boundary = [];

var flat_view_index = 0;
var file_name = undefined;

var call_stack = [];

var global_row_index = 0;
var grapth_row_index = 0;

function is_element_visible(child, parrent) {
	if(child == undefined || parrent == undefined){
		return [true, true];
	}
	var parrent_location = parrent.getBoundingClientRect();
	var child_location = child.getBoundingClientRect();
	
	var top = child_location.top - child_location.height;
	var bottom = child_location.bottom - child_location.height;

	var isVisible = (top >= 0) && (bottom <= parrent_location.height);
	return [isVisible, bottom <= parrent_location.height];
}


function moving_rows(table_row, keep_row){
	if(table_row != undefined){
		var current_space = parseInt(table_row.children[0].innerText, 16);	
			
		var new_section = table_row.getAttribute("section");
		var new_boundary = false;
		
		if(boundary.length == 0){
			new_boundary = true;
		}else if(0 < boundary.length){
			new_boundary = (!( (boundary[0] <= current_space)  && (current_space <= boundary[1])));
		}

		if(new_boundary){
			console.log("refresh!");
			socket.emit('give_grapth', {
				"section":table_row.getAttribute("section"),
				"address":table_row.getAttribute("name")
			});
		}

		var target = document.getElementsByName(table_row.getAttribute("name"));
		ligther.highlight(target);
		if(keep_row == undefined){
			global_row_index = target[0].rowIndex;
			if(1 < target.length){
				grapth_row_index = target[1].rowIndex;
			}
			call_stack = [];
		}

		socket.emit("dynamic_info", {
				data:{
					"address":table_row.getAttribute("name").replace("row_", "")
				}
		});
	}
}


var delta_text = undefined;
var text_element = undefined;

window.addEventListener("focus", function(e) {
	if(document.activeElement.nodeName == "SPAN"){
		delta_text = document.activeElement.innerText;
		text_element = document.activeElement;
		text_element.innerText  = document.activeElement.innerText;
	}
}, true);

window.addEventListener("blur", function(e) {
	if(text_element != undefined){
		//	report the change ...
		//	need a good way to store all changes....
		//	I want to be able to undo stuff I did last time I had the document open....		
		if(text_element.parentElement.id == "code_cell"){
			text_element.innerHTML = code_highlighter(text_element.innerText, Array.from(all_registers));
		//	console.log("I just reparse everything ?");
		}
		else if(text_element.innerText != delta_text){
			var address = (text_element.parentElement.parentElement.id.replace("flat_view_row_", ""));
			var jsonobj = [address, text_element.innerText];
			socket.emit("comments", {data:jsonobj})
			text_element = undefined;
		}
	}
}, true);


window.addEventListener("keydown", function(e) {
	
	if(document.activeElement.nodeName == "SPAN"){
		if(document.activeElement.parentElement.id == "comment"){
		//	console.log("changing comment ey?");
		//	console.log(document.activeElement.innerText);
		}
	}
	// space and arrow keys
	/*if(e.keyCode == 32){
		if(document.activeElement.nodeName == "TABLE"){
		//	var target = document.activeElement.rowIndex;
			var target_row = document.activeElement.rows[flat_view_index];
//			console.log(target_row);
			if(target_row.getAttribute("refrence_section") != undefined){
				var new_section_name = prompt("What is the new name?");
				var old_name = target_row.children[0].innerText;
						
				if(!table_was_build){
					build_table();
					table_was_build = true;
				}

				console.log("search_" + old_name);
				console.log(document.getElementById("search_" + old_name));
				document.getElementById("search_" + old_name).innerHTML = new_section_name;

				target_row.children[0].innerText = new_section_name;
				e.preventDefault();
			}
		}
	}*/

	if(38 <= e.keyCode <= 40 && document.activeElement.nodeName != "SPAN"){
		var index = global_row_index;
		var flat_view = true;
		if(document.activeElement.getAttribute("name") == "graph_table_code"){
			index = grapth_row_index;
			flat_view = false;
		}

		function move_2_edge(mode){
			var id = document.activeElement.parentElement.id;
			var edges = refrence_key_node[id];
			console.log(edges);
			if(edges != undefined && 0 < edges.length){
				var target = undefined;
				if(mode == "DOWN" && edges.length == 1){
					target = edges[0];
				}else if(mode == "LEFT"){
					target = edges[0];
				}else if(mode == "RIGTH"){
					target = edges[edges.length - 1];
				}

				if(target != undefined){
					call_stack.push(id);
					move_2_node(target.children[0]);
					return true;
				}
			}
			return false;
		}

		// up and down
		if(e.keyCode == 38){
			e.preventDefault();
			if(0 <= (index - 1)){
				index -= 1;
				var target_row = document.activeElement.rows[index];
				var target = document.getElementsByName(target_row.getAttribute("name"));
				moving_rows(target[0], false);			
			}else if(!flat_view){
				var target = call_stack.pop();
				if(target != undefined){
					var element = document.getElementById(target).children[0];
					move_2_node(element, element.rows.length - 1);
					index = element.rows.length - 1;
				}
			}
		}


		if(e.keyCode == 40){
			e.preventDefault();

			var target_element = document.activeElement.rows;
			if((index + 1) < target_element.length){
				index += 1;
				var target_row = target_element[index];
				var target = document.getElementsByName(target_row.getAttribute("name"));
				moving_rows(target[0], false);
			}else{	
				if(move_2_edge("DOWN")){
					index = 0;
				}
			}
		}

		//	left and rigth
		if(document.activeElement.getAttribute("name") == "graph_table_code"){
			if(e.keyCode == 37){
				e.preventDefault();
				if(move_2_edge("LEFT")){
					index = 0;
				}
			}
			if(e.keyCode == 39){
				e.preventDefault();			
				if(move_2_edge("RIGTH")){
					index = 0;
				}
			}
		}


		if(document.activeElement.getAttribute("name") == "graph_table_code"){
			grapth_row_index = index;
		}else{
			global_row_index = index;
		}
		

	}
}, false);



function hide_hex(){
	var target_element = document.getElementsByName("hex_view")[0];
	if(target_element.style.display == "none"){
		target_element.style.display = "block";
	}else{
		target_element.style.display = "none";
	}
}

function hide_grapth(){
	var target_element = document.getElementsByName("grapth-div")[0];
	if(target_element.style.display == "none"){
		target_element.style.display = "block";
	}else{
		target_element.style.display = "none";
	}
}

function save_project(){
	if(file_name == undefined){
		var new_file_name = prompt("Save project as ?");
		if(new_file_name.length > 0){
			file_name = new_file_name;
		}
	}
	socket.emit('save', {data:{"file_name":file_name}});
}

function move_2_node(target, index){
	if(index == undefined){
		index = 0;
	}
//	console.log(target.table_reference);
	//document.getElementsByName(target.table_reference.rows[index].getAttribute("name");
	//target.table_reference.rows[index].click();
	target.focus();
	moving_rows(target.rows[index], false);
}	


function jump_2_node(row){
	if(document.getElementById("grapth_" + row.innerHTML) != null){
		document.getElementById("grapth_" + row.innerHTML).scrollIntoView();
	}else{
		var target = document.getElementsByName("row_" + row.innerHTML)[0];
		target.click();
		target.scrollIntoView();
		
		var new_target = document.getElementsByName(row.getAttribute("name"))[0];
		add_element_history(new_target, false);
	}
}

function find_node(row){
/*	if(document.getElementById("grapth_" + row.innerHTML.split(" ")[1]) != null){
		document.getElementById("grapth_" + row.innerHTML).scrollIntoView();
	}else{*/

	var target_element = row.getAttribute("jmp_target");
		
	var target = document.getElementsByName(target_element);
	if(1 < target.length){
		target[1].scrollIntoView();
	}
	target[0].click();
	target[0].scrollIntoView();
		
	var old_target = row;
	add_element_history(old_target, false);
//	}
}

function highlight(e){
	if(document.getElementById("grapth_" + e.innerHTML) != null){
		document.getElementById("grapth_" + e.innerHTML).parentElement.style.background = "red";
	}
}

function highlight_low(e){
	if(document.getElementById("grapth_" + e.innerHTML) != null){
		document.getElementById("grapth_" + e.innerHTML).parentElement.style.background = "";
	}
}


document.addEventListener('click', function(e){
	if(e.target.tagName == "TD" || e.target.tagName == "TR"){
		var target = e.target;
		if(e.target.tagName == "TD"){
			target = e.target.parentElement;
		}
//		target.style.background = "red";
		moving_rows(target);
		//console.log(target);
	}
});







