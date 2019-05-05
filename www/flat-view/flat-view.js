
var last_target = -1;
var look_up_row = {

};
var all_registers = new Set([]);
var current_section = undefined;


var code_comments = {

}

var code_sections = {

}

function create_table_row(row_name, section, address, code, size){
	var table = document.getElementById("flat_view_table");
	var row = table.insertRow(-1);

	if(address == undefined){
		row.setAttribute("name", "row_" + section);
	}else{
		row.setAttribute("name", "row_" + address);
	}

	row.setAttribute("id", "flat_view_row_" + address);
	row.setAttribute("onClick", "moving_rows(this)");
	row.setAttribute("type", "flat");


	var section_cell = row.insertCell(0);

	if(section != undefined){
		section_cell.innerHTML = section;
		current_section = section;
		row.setAttribute("id", "section");
	}

	row.setAttribute("section", current_section);

	if(address == undefined && code == undefined){
		return undefined;
	}

	var address_cell = row.insertCell(1);
	address_cell.innerHTML = address;
	address_cell.id = "address_cell";

	var code_cell = row.insertCell(2);
	
	var code_content = document.createElement("span");
	code_content.setAttribute("contenteditable", "true");
	code_content.innerHTML = code[0] + "\t" + code_highlighter(code[1], code[2]);
	code_content.setAttribute("contenteditable", "true");
	
	code_cell.innerHTML = code_content.outerHTML;
	code_cell.id = "code_cell";


	/*
		comment cell
	*/
	var comment_cell = row.insertCell(3);
	comment_cell.id = "comment";
	var span_comment = document.createElement("span");
	span_comment.setAttribute("contenteditable", "true");
	if(code_comments.hasOwnProperty(address)){
		span_comment.innerHTML = code_comments[address];
	}
	comment_cell.innerHTML = span_comment.outerHTML;
	row.setAttribute("start", size[0]);
	row.setAttribute("end", size[1]);
}


function create_flat_view(msg){
	var table = document.getElementById("flat_view_table");
	table.setAttribute("tabindex", "0");
	if(table.rows.length == 1){
		var row_name = undefined;
		var section_size = Object.keys(msg);
		for(var i = 0; i < section_size.length; i++){
			var section_index = section_size[i];
			var section_name = msg[section_size[i]][0];
			
			var section_code = msg[section_size[i]][1];
			var section_addreses = Object.keys(section_code);
		
			create_table_row(section_name, section_name, undefined, undefined, undefined);

			var instruction_position = 0;
			var padding = code_sections[section_name][0];
			for(var address_index = 0; address_index < section_addreses.length; address_index++){
				var instruction_size = undefined;
				if((address_index + 1) < section_addreses.length){
					instruction_size = (parseInt(section_addreses[address_index + 1], 16) - parseInt(section_addreses[address_index], 16));
				}else{
					instruction_size = code_sections[section_name][1] - instruction_position;
				}

				create_table_row(section_name, undefined, section_addreses[address_index], section_code[section_addreses[address_index]], [padding + instruction_position, padding + instruction_position + instruction_size ]);
				instruction_position += instruction_size;
			}
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









