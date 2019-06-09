


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

//var last_section = ".init";

var boundary = [];

function moving_rows(table_row, keep_row){
	/*if(table_row != undefined && table_row.getAttribute("type") == "flat"){
		var old_target = target_section;
		target_section = table_row.getAttribute("section");
		
		var section = table_row.getAttribute("refrence_section");
		if(section == undefined){
			section = look_up_section(table_row.getAttribute("name").replace("row_", ""));
		}

		if(section != undefined && section != last_index || old_target != target_section){
			if(old_target != target_section){
				create_grapth(last_message, 0, false);
				call_stack = [];
			}else{
				create_grapth(last_message, section, false);
				call_stack = [];
			}
			document.getElementsByName("grapth-div")[0].scroll(0, 0);
		}

		var targets_hex_view = [];
		for(var i = table_row.getAttribute("start"); i < table_row.getAttribute("end"); i++){
			var results = document.getElementsByName(i);
			for(var j = 0; j < results.length; j++){
				targets_hex_view.push(results[j]);
			}
		}
		if(targets_hex_view.length > 0 && targets_hex_view[0] != undefined){
			targets_hex_view[0].scrollIntoView();
			hex_ligther.highlight(targets_hex_view);
		}	
		flat_view_index = table_row.rowIndex;
	}else{
		global_row_index = table_row.rowIndex;
	}
*/
	
	console.log(table_row);
	if(table_row != undefined){
		var new_section = table_row.getAttribute("section");
		if(new_section != undefined){
			var current_space = parseInt(table_row.children[0].innerText, 16);	
			var new_boundary = false;
			if(boundary == undefined){
				new_boundary = true;
			}else if(0 < boundary.length){
				new_boundary = (!( (boundary[0] < current_space)  && (current_space < boundary[1])));
			}
			
			if(target_section != new_section || new_boundary){
				target_section = new_section;

				var section_target = address_section[new_section];
				if(section_target != undefined){
					var target_space = Object.keys(section_target);
					if(target_space.length == 0){
						create_grapth(last_message, 0, false);
						boundary = undefined;
					}else{
						for(var i = 0; i < target_space.length; i++){
							if(current_space < parseInt(target_space[i], 16)){
								console.log([current_space , target_space[i]]);
								create_grapth(last_message, (address_section[new_section][target_space[i]] - 1), false);
								if(i == 0){
									boundary = [0, parseInt(target_space[i], 16)];
								}else{
									boundary = [parseInt(target_space[i - 1], 16), parseInt(target_space[i], 16)];
								}
								break;
							}
						}
					}
				}					
			}
		}

		var target = document.getElementsByName(table_row.getAttribute("name"));
		ligther.highlight(target);
		if(keep_row == undefined){
			global_row_index = target[0].rowIndex;
			grapth_row_index = target[1].rowIndex;
			call_stack = [];
			console.log([global_row_index, grapth_row_index]);
		}

		/*
		var status = is_element_visible(target[0], document.getElementsByName("flat-view-div")[0]);
		if(!status[0]){
			document.getElementById("flat_view_table").rows[table_row.rowIndex].scrollIntoView(false);//status[1]);
		}

		socket.emit("dynamic_info", {
				data:{
					"address":table_row.getAttribute("name").replace("row_", "")
				}
		});
		global_row_index = table_row.rowIndex;
		*/


	//	console.log("hwat is rong2");
	//	console.log(global_row_index);
	//	console.log(table_row.rowIndex);
		/*
		if(target[0].getAttribute("id") != "section"){
			var status = is_element_visible(target[1], document.getElementsByName("grapth-div")[0]);
			if(!status[0]){
				target[1].scrollIntoView(false);
			}
		}*/
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

	if(e.keyCode == 32){
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
				//	element.setAttribute("id", "search_" + block_list[key]);

				e.preventDefault();
			}
//			console.log(target_row);
		}

		//	alert("change the name of the section?");

	}

	if(38 <= e.keyCode <= 40  && document.activeElement.nodeName != "SPAN"){
		// space and arrow keys
		// up and down

	//	console.log(global_row_index);
	//	console.log("wut");

		var index = global_row_index;
		var flat_view = true;
		if(document.activeElement.getAttribute("name") == "grapth_table_code"){
			index = grapth_row_index;		
			flat_view = false;
		}
		console.log([global_row_index, grapth_row_index]);

		// up and down
		/*function move_up(){

		}*/
		
		if(e.keyCode == 38){
			e.preventDefault();
			if(0 <= (index - 1)){
				index -= 1;
				var target_row = document.activeElement.rows[index];
		//		console.log(target_row);
				var target = document.getElementsByName(target_row.getAttribute("name"));
				moving_rows(target[0], false);			
			}else if(!flat_view){
				var target = call_stack.pop();
				if(target != undefined){
					var element = refrence_key_node[target].table_reference;
					move_2_node(refrence_key_node[target], element.rows.length - 1);
					index = element.rows.length - 1;
				}
			}
		}

		if(e.keyCode == 40){
			e.preventDefault();
			console.log(index);
			var target_element = document.activeElement.rows;//[index];
//			console.log(target_element);
			if((index + 1) < target_element.length){
				index += 1;
				var target_row = target_element[index];
				var target = document.getElementsByName(target_row.getAttribute("name"));
				moving_rows(target[0], false);
			}else{				
				var id = document.activeElement.id;//.replace("table", "");
				var edges = refrence_key_node[id];

				if(edges != undefined){
					edges = edges["edges"];
					if(edges.length == 1){
						var target = edges[0];
						call_stack.push(id);
						move_2_node(target);
						index = 0;
					}
				}
			}
		}

		//	left and rigth
		if(document.activeElement.getAttribute("name") == "grapth_table_code"){
			if(e.keyCode == 37){
				e.preventDefault();
				var id = document.activeElement.id;//document.activeElement.getAttribute("name");//.replace("table", "");
				console.log(refrence_key_node);
				var edges = refrence_key_node[id];
				console.log(edges);
				if(edges != undefined){
					edges = edges["edges"];
					if(edges.length > 0){
						var target = edges[0];
						call_stack.push(id);
						move_2_node(target);
						index = 0;
					}
				}
			}
			if(e.keyCode == 39){
				e.preventDefault();			
				var id = document.activeElement.id;//.replace("table", "");
				console.log(refrence_key_node);
				var edges = refrence_key_node[id];
				console.log(edges);
				if(edges != undefined){
					edges = edges["edges"];
					if(edges.length > 0){
						var target = edges[edges.length - 1];
						call_stack.push(id);
						move_2_node(target);
						index = 0;
					}
				}
			}
		}


		if(document.activeElement.getAttribute("name") == "grapth_table_code"){
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
	target.table_reference.focus();
	moving_rows(target.table_reference.rows[index], false);
}	


function jump_2_node(row){
	if(document.getElementById("grapth_" + row.innerHTML) != null){
		document.getElementById("grapth_" + row.innerHTML).scrollIntoView();
	}else{
		var target = document.getElementsByName("row_" + row.innerHTML)[0];
		target.click();
		target.scrollIntoView();
		
		var new_target = document.getElementsByName(row.parentElement.getAttribute("name"))[0];
		add_element_history(new_target, false);
	}
}

function find_node(row){
/*	if(document.getElementById("grapth_" + row.innerHTML.split(" ")[1]) != null){
		document.getElementById("grapth_" + row.innerHTML).scrollIntoView();
	}else{*/

	var target_element = row.getAttribute("jmp_target");
		
	var target = document.getElementsByName("row_" + target_element)[0];
	target.click();
	target.scrollIntoView();
		
	var new_target = document.getElementsByName(row.parentElement.parentElement.getAttribute("name"))[0];
	add_element_history(new_target, false);
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







