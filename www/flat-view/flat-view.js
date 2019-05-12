
var last_target = -1;
var look_up_row = {

};
var all_registers = new Set([]);
var current_section = undefined;


var code_comments = {

}

var code_sections = {

}

function init_section(section, index){
	var table = document.getElementById("flat_view_table");
	var row = table.insertRow(index);

	row.setAttribute("name", "row_" + section);
	row.setAttribute("onClick", "moving_rows(this)");
	row.setAttribute("type", "flat");


	var section_cell = row.insertCell(0);
	section_cell.innerHTML = section;
	current_section = section;
	row.setAttribute("id", "section");
	row.setAttribute("section", current_section);
	return row;
}

function create_table_row(section, address, code, size){
	var table = document.getElementById("flat_view_table");
	var row = table.insertRow(-1);

	row.setAttribute("id", "flat_view_row_" + address);
	row.setAttribute("onClick", "moving_rows(this)");
	row.setAttribute("type", "flat");
	row.setAttribute("section", current_section);
	row.setAttribute("name", "row_" + address);

	var section_cell = row.insertCell(0);


	var address_cell = row.insertCell(1);
	address_cell.innerHTML = address;
	address_cell.id = "address_cell";

	var code_cell = row.insertCell(2);
	var code_content = document.createElement("span");
//	code_content.setAttribute("contenteditable", "true");
	code_content.innerHTML = code["instruction"] + "\t" + code_highlighter(code["argument"], code["registers"]);
//	code_content.setAttribute("contenteditable", "true");
	
	//	basic parsing of target
	if(code["argument"][0] == "0" && code["argument"][1] == "x"){
		code_content.setAttribute("ondblclick", "find_node(this)");
		code_content.setAttribute("jmp_target", code["argument"]);
	}


	code_cell.innerHTML = code_content.outerHTML;
	code_cell.id = "code_cell";

	/*
		comment cell
	*/
	var comment_cell = row.insertCell(3);
	comment_cell.id = "comment";
	var span_comment = document.createElement("span");
//	span_comment.setAttribute("contenteditable", "true");
	
	span_comment.innerHTML = code["comment"];

	/*
	if(code_comments.hasOwnProperty(address)){
		span_comment.innerHTML = code_comments[address];
	}
	*/
	comment_cell.innerHTML = span_comment.outerHTML;
	row.setAttribute("start", size[0]);
	row.setAttribute("end", size[1]);
}


function create_flat_view(msg){
	var table = document.getElementById("flat_view_table");
	table.setAttribute("tabindex", "0");

	var section_size = Object.keys(msg);
	
	for(var i = 0; i < section_size.length; i++){
		//	this is the section
		var section_index = section_size[i];
		var section_name = msg[section_index]["section_name"];

		//	check if it is already created
		if(document.getElementsByName("row_" + section_name).length > 0){
			continue;
		}
		
		var section_code = msg[section_index]["code"];
		var section_addreses = Object.keys(section_code);
		
		init_section(section_name, -1);

		var instruction_position = 0;
		var padding = code_sections[section_name][0];
		for(var address_index = 0; address_index < section_addreses.length; address_index++){
			var instruction_size = undefined;
			var address = section_addreses[address_index];
			if((address_index + 1) < section_addreses.length){
				var address_plus_one =  section_addreses[address_index + 1];
				instruction_size = section_code[address_plus_one]["address_int"] - section_code[address]["address_int"];
			}else{
				instruction_size = code_sections[section_name][1] - instruction_position;
			}

			var size = [padding + instruction_position, padding + instruction_position + instruction_size];
			create_table_row(undefined, section_addreses[address_index], section_code[address], size);

			instruction_position += instruction_size;
		}
	}


	socket.on('size response', function( msg ) {
		//	note: you should actually readjust every address .....
		// 	n_i = n_i-1 + size

		/*
		var prev_target_element = document.getElementById("flat_view_table").rows[msg["target"] - 1];
		var next_address = parseInt(prev_target_element.children[1].innerHTML, 16) + msg["size"];

		var target_element = document.getElementById("flat_view_table").rows[msg["target"]];
		target_element.children[1].innerHTML = "0x" + next_address.toString(16);*/
	});
}









