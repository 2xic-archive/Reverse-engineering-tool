
var last_target = -1;
var look_up_row = {

};
var all_registers = new Set([]);
var current_section = undefined;


var code_comments = {

}

var code_sections = {

}

function parse(current, registers){
	var current_text = current;
	if(registers.length == 0){
		registers.push("fake");
	}/*else{
		//	for(var i = 0; i < )
		//	all_registers = all_registers.concat(registers);
	}*/

	for(var i = 0; i < registers.length; i++){
		var word_length = registers[i].length;
		var word = registers[i];
		var key_word_index = 0;
		
		var refrence_count = 0;
		var searching = true;

		var j = 0;
		var size = current_text.length;

		var hex_mode = false;
		var hex_start = 0;

		if(word != "fake"){
			all_registers.add(word);
		}

		while(j < size){
			if(current_text[j] == "<"){
				refrence_count += 1;
			}
			if(current_text[j] == ">"){
				refrence_count -= 1;
			}

			if(current_text[j] == "0"){
				if((j + 1) < size){
					if(current_text[j + 1] == "x"){
						hex_mode = true;
						hex_start = j;
					}
				}
			}

			if(word[key_word_index] == current_text[j] && searching && refrence_count == 0){
				key_word_index += 1;
				if(key_word_index == word_length){
					if(refrence_count == 0){
						var span_end = "</span>";
						var span_start = "<span style='color:red;' contenteditable='true' key='" + word +"'>";
						current_text = current_text.insert(j + 1, span_end);
						current_text = current_text.insert(j - word_length + 1, span_start);

						size += span_start.length + span_end.length;
						j += (span_start.length + span_end.length);// + 1;
					}else{
						console.log("hm");
					}
				}
			}else{
				key_word_index = 0;
				searching = false;
			}

			if(current_text[j] == " " || current_text[j] == "[" || current_text[j] == "]" || current_text[j] == ","){
				searching = true;
				if(hex_mode){
					var span_end = "</span>";
					var span_start = "<span style='color:blue;' key='" + "hex" +"'>";
					current_text = current_text.insert(j, span_end);
					current_text = current_text.insert(hex_start, span_start);

					size += span_start.length + span_end.length;
					j += (span_start.length + span_end.length);// 		
					hex_mode = false;
				}
			}
			j++;
		}
		if(hex_mode){
			var span_end = "</span>";
			var span_start = "<span style='color:blue;' key='" + "hex" +"'>";
			current_text = current_text.insert(j, span_end);
			current_text = current_text.insert(hex_start, span_start);

			size += span_start.length + span_end.length;
			j += (span_start.length + span_end.length);// 		
			hex_mode = false;
		}
	}
	return current_text;
}

function create_table_row(row_name, section, address, code, size){
	var table = document.getElementById("flat_view_table");
	var row = table.insertRow(-1);

	//row.setAttribute("name", row_name);
	if(address == undefined){
		row.setAttribute("name", "row_" + section);
	}else{
		row.setAttribute("name", "row_" + address);
	}

	row.setAttribute("id", "flat_view_row_" + address);
	row.setAttribute("onClick", "moving_rows(this)");
	row.setAttribute("type", "flat");

	if(section != undefined){
		row.setAttribute("id", "section");
	}

	var section_cell = row.insertCell(0);

	if(section != undefined){
		section_cell.innerHTML = section;
		current_section = section;
	}

	row.setAttribute("section", current_section);

	if(address == undefined && code == undefined){
		return;
	}

	var address_cell = row.insertCell(1);
	address_cell.innerHTML = address;
	address_cell.id = "address_cell";


	var code_cell = row.insertCell(2);
	var instruction = document.createElement("span");
	var instruction_args = document.createElement("span");
	instruction_args.setAttribute("contenteditable", "true");


	instruction.innerHTML = code[0] + "\t";
	instruction.setAttribute("id", "instruction");
	instruction.setAttribute("contenteditable", "true");

	var new_code = code[1];

	String.prototype.insert = function (index, string) {
		if (index > 0){
			return this.substring(0, index) + string + this.substring(index, this.length);
		}
//		return undefined;
		return string + this;
	};


	instruction_args.innerHTML = code[0] + "\t" + parse(new_code, code[2]);
	instruction_args.setAttribute("id", "instruction_args");
	instruction_args.setAttribute("contenteditable", "true");

	//input_code_cell.setAttribute("value", code.join("\t"));
	//input_code_cell.setAttribute("readonly", "true");

	code_cell.id = "code_cell";
	code_cell.innerHTML = instruction_args.outerHTML;


	var comment_cell = row.insertCell(3);
	comment_cell.id = "comment";

	if(code_comments.hasOwnProperty(address)){
		//alert(1);
		var span_comment = document.createElement("span");
		span_comment.innerHTML = code_comments[address];
		span_comment.setAttribute("contenteditable", "true");
		comment_cell.innerHTML = span_comment.outerHTML;
	}else{		
		var span_comment = document.createElement("span");
//		span_comment.innerHTML = code_comments[address];
		span_comment.setAttribute("contenteditable", "true");
		comment_cell.innerHTML = span_comment.outerHTML;
	}

	row.setAttribute("start", size[0]);
	row.setAttribute("end", size[1]);

	/*
	if(comment != undefined){
		var span_comment = document.createElement("span");
		span_comment.innerHTML = comment;
		span_comment.setAttribute("contenteditable", "true");
		comment_cell.innerHTML = span_comment.outerHTML;
	}

	*/

	//	span transfer to input ? not sure...
	/*
	$("input").dblclick(function(){
		this.current = this.value;
		this.sent = false;
		this.readOnly='';
	});

	$("input").dblclick(function(){
		this.current = this.value;
		this.sent = false;
		this.readOnly='';
	});


	$("input").click(function(ye){
		if(last_target != -1){
			for(var x = 0; x < last_target.children.length; x++){
				last_target.children[x].style.borderBottom = "";
				last_target.children[x].style.borderTop = "";
				
			}				
		}
		var target = ye.toElement.parentElement.parentElement;
		for(var x = 0; x < target.children.length; x++){
			target.children[x].style.borderBottom = "1pt solid black";
			target.children[x].style.borderTop = "1pt solid black";
			
		}
		last_target = target;
	});


	$("input").focusout(function() {
		String.prototype.trim = function() {
			return String(this).replace("\t"," ");
		};
		if(this.current != this.value && !this.sent){
			var name_section = (this.parentElement.parentElement.getAttribute("name"));
			var sections = document.getElementsByName(name_section);
			var code = [name_section];
			for(var i = 0; i < sections.length; i++){
				if(sections[i].children.length > 1){
					code.push(sections[i].children[2].children[0].value);
				}
			}
			socket.emit('assemble instruction', {data:code});
			this.sent = true;
		}
		this.setAttribute("readonly", "true");
	});

	$("tr").keydown(function(event) {
	    if(event.ctrlKey && event.keyCode == 78) {
	    	socket.emit('get instruciton size', {data:["nop;", this.rowIndex + 1]});
	    	create_table_row(this.getAttribute("name"), "", "", "nop", this.rowIndex + 1);
		}
	});*/

/*
		$("input").click(function(ye){
		if(last_target != -1){
			for(var x = 0; x < last_target.children.length; x++){
				last_target.children[x].style.borderBottom = "";
				last_target.children[x].style.borderTop = "";
				
			}				
		}
		var target = ye.toElement.parentElement.parentElement;
		for(var x = 0; x < target.children.length; x++){
			target.children[x].style.borderBottom = "1pt solid black";
			target.children[x].style.borderTop = "1pt solid black";
			
		}
		last_target = target;
	});
*/
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
			for(var j = 0; j < section_addreses.length; j++){
				/*if(section_code[section_addreses[j]].length == 4){
					create_table_row(section_name, undefined, section_addreses[j], section_code[section_addreses[j]], section_code[section_addreses[j]][3]);	
					look_up_row[section_addreses[j][0]] = table.rows[table.rows.length - 1];
				}else{
				*/
				var instruction_size = undefined;
				if((j + 1) < section_addreses.length){
					instruction_size = (parseInt(section_addreses[j + 1], 16) - parseInt(section_addreses[j], 16));
				}else{
					instruction_size = code_sections[section_name][1] - instruction_position;
				}
				if(section_code[section_addreses[j]].length == 1){
					console.log(section_addreses[j]);
				}
				if(section_addreses[j] == undefined){
					console.log("i cry");
					alert(1);
				}
				if(section_code[section_addreses[j]] == undefined){
					console.log("da fak");
				}
				create_table_row(section_name, undefined, section_addreses[j], section_code[section_addreses[j]], [padding + instruction_position, padding + instruction_position + instruction_size ]);	

				instruction_position += instruction_size;
			}
		}
	}


	socket.on('size response', function( msg ) {
		//	note you should actually readjust evrey address .....
		// 	n_i = n_i-1 + size

		var prev_target_element = document.getElementById("flat_view_table").rows[msg["target"] - 1];
		var next_address = parseInt(prev_target_element.children[1].innerHTML, 16) + msg["size"];

		var target_element = document.getElementById("flat_view_table").rows[msg["target"]];
		target_element.children[1].innerHTML = "0x" + next_address.toString(16);
	});
}









