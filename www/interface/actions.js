



function moving_rows(e){
	if(e.getAttribute("type") == "flat"){
		var old_target = target_section;
		target_section = e.getAttribute("section");
		//	console.log(target_section);
		var section = look_up_section(e.getAttribute("name").replace("row_", ""));
		if(section != last_index || old_target != target_section){
			create_grapth(last_message, section);
			document.getElementsByName("grapth-div")[0].scroll(0, 0);
		}
	}else{
		console.log(e.rowIndex);
		global_row_index = e.rowIndex;
	}
	console.log(e.rowIndex);

	var last_target = e.rowIndex;
	var target = document.getElementsByName(e.getAttribute("name"));
	ligther.highligth(target);
}

/*
$("tr").click(function(e){
		if(this.getAttribute("type") == "flat"){
			var old_target = target_section;
			target_section = this.getAttribute("section");
		//	console.log(target_section);
			var section = look_up_section(this.getAttribute("name").replace("row_", ""));
			if(section != last_index || old_target != target_section){
				create_grapth(last_message, section);
				document.getElementsByName("grapth-div")[0].scroll(0, 0);
			}
		}else{
			console.log(this.rowIndex);
			global_row_index = this.rowIndex;
		}
		var last_target = this.rowIndex;
		var target = document.getElementsByName(this.getAttribute("name"));
		ligther.highligth(target);
	});
*/

var call_stack = [];

window.addEventListener("keydown", function(e) {
	// space and arrow keys
	// up and down
	
	if(e.keyCode == 38){
		e.preventDefault();
		if(0 <= (global_row_index - 1)){
			global_row_index -= 1;
			var target_row = document.activeElement.rows[global_row_index];
			var target = document.getElementsByName(target_row.getAttribute("name"));
			ligther.highligth(target);
		}else{
			var target = call_stack.pop();
			if(target != undefined){
				var element = refrence_key_node[target].table_reference;
				move_2_node(refrence_key_node[target], element.rows.length - 1);
			}
		}
	}
	if(e.keyCode == 40){
		e.preventDefault();
		var target_element = document.activeElement.rows;
		if((global_row_index + 1) < target_element.length){
			global_row_index += 1;
			var target_row = target_element[global_row_index];
			var target = document.getElementsByName(target_row.getAttribute("name"));
			ligther.highligth(target);
		}
	}
	//	left and rigth
	if(e.keyCode == 37){
		var id = document.activeElement.id.replace("table", "");
		var edges = refrence_key_node[id]["edges"];
		if(edges.length > 0){
			var target = edges[0];
			call_stack.push(id);
			move_2_node(target);
		}
	}
	if(e.keyCode == 39){
		var id = document.activeElement.id.replace("table", "");
		var edges = refrence_key_node[id]["edges"];
		if(edges.length > 0){
			var target = edges[edges.length - 1];
			call_stack.push(id);
			move_2_node(target);
		}
	}
}, false);

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
