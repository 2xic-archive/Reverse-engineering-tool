


var flat_view_index = 0;
var file_name = undefined;


function moving_rows(e){
	if(e.getAttribute("type") == "flat"){
		var old_target = target_section;
		target_section = e.getAttribute("section");
		
		var section = look_up_section(e.getAttribute("name").replace("row_", ""));
		if(section != last_index || old_target != target_section){
			create_grapth(last_message, section);
			document.getElementsByName("grapth-div")[0].scroll(0, 0);
		}

		var targets_hex_view = [];
		for(var i = e.getAttribute("start"); i < e.getAttribute("end"); i++){
			var results = document.getElementsByName(i);
			for(var j = 0; j < results.length; j++){
				targets_hex_view.push(results[j]);
			}
		}
		if(targets_hex_view.length > 0 && targets_hex_view[0] != undefined){
			targets_hex_view[0].scrollIntoView();
			console.log(targets_hex_view);
			hex_ligther.highligth(targets_hex_view);

		}	
		flat_view_index = e.rowIndex;
	}else{
		global_row_index = e.rowIndex;
	}
	var last_target = e.rowIndex;
	var target = document.getElementsByName(e.getAttribute("name"));
	ligther.highligth(target);
}


var call_stack = [];

var delta_text = undefined;
var text_element = undefined;

window.addEventListener("focus", function(e) {
	if(document.activeElement.nodeName == "SPAN"){
//		if(document.activeElement.parentElement.id == "code_cell"){
//		}else{
			delta_text = document.activeElement.innerText;
			text_element = document.activeElement;
			text_element.innerText  = document.activeElement.innerText;
//		}
	}
}, true);

window.addEventListener("blur", function(e) {
	if(text_element != undefined){
		//	report the change ...
		//	need a good way to store all changes....
		//	I want to be able to undo stuff I did last time I had the document open....		
		if(text_element.parentElement.id == "code_cell"){
			text_element.innerHTML = parse(text_element.innerText, Array.from(all_registers));
			console.log("I just reparse evreything ?");
		}
		else if(text_element.innerText != delta_text){
			var address = (text_element.parentElement.parentElement.id.replace("flat_view_row_", ""));
			var jsonobj = [address, text_element.innerText];
			socket.emit("comments", {data:jsonobj})

			text_element = undefined;
		}
	}
}, true);

/*
window.addEventListener("onblur", function(e) {
	console.log(e);
});
*/

/*
window.addEventListener("keydown", function(e) {
	if(document.activeElement.nodeName == "SPAN"){
		if(document.activeElement.parentElement.id == "comment"){
			console.log("chaning comment ey?");
			console.log(document.activeElement.innerText);
		}

	}
	if(38 <= e.keyCode <= 39 && document.activeElement.nodeName != "SPAN"){
		// space and arrow keys
		// up and down
		var index = global_row_index;
		if(document.activeElement.id == "flat_view_table"){
			index = flat_view_index;		
		}

		// up and down
		if(e.keyCode == 38){
			e.preventDefault();
			if(0 <= (index - 1)){
				index -= 1;
				var target_row = document.activeElement.rows[index];
				var target = document.getElementsByName(target_row.getAttribute("name"));
				ligther.highligth(target);
			}else{
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
			var target_element = document.activeElement.rows;
			if((index + 1) < target_element.length){
				index += 1;
				var target_row = target_element[index];
				var target = document.getElementsByName(target_row.getAttribute("name"));
				ligther.highligth(target);
			}
		}
			
		//	left and rigth
		if(!(document.activeElement.id == "flat_view_table")){
			e.preventDefault();
			if(e.keyCode == 37){
				var id = document.activeElement.id.replace("table", "");
				var edges = refrence_key_node[id]["edges"];
				if(edges.length > 0){
					var target = edges[0];
					call_stack.push(id);
					move_2_node(target);
					global_row_index = 0;
				}
			}
			
			if(e.keyCode == 39){
				var id = document.activeElement.id.replace("table", "");
				var edges = refrence_key_node[id]["edges"];
				if(edges.length > 0){
					var target = edges[edges.length - 1];
					call_stack.push(id);
					move_2_node(target);
					global_row_index = 0;
				}
			}
		}

		if(document.activeElement.id != "flat_view_table" && !(e.keyCode == 37 || e.keyCode == 39)){
			global_row_index = index;
		}else{
			flat_view_index = index;
		}
	}
//	console.log("hm");
}, false);

*/


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
	target.table_reference.rows[index].click();
	target.table_reference.focus();
}

function highligth(e){
	if(document.getElementById("grapth_" + e.innerHTML) != null){
		document.getElementById("grapth_" + e.innerHTML).parentElement.style.background = "red";
	}
}

function highligth_low(e){
	if(document.getElementById("grapth_" + e.innerHTML) != null){
		document.getElementById("grapth_" + e.innerHTML).parentElement.style.background = "";
	}
}
