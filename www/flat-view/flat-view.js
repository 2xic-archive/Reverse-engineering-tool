
var last_target = -1;


var current_section = undefined;


function parse(current, registers){
	var current_text = current;
	if(registers.length == 0){
		registers.push("fake");
	}
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

function create_table_row(row_name, section, address, code, index){
	var table = document.getElementById("flat_view_table");
		
	if(index == -1){
		index = table.rows.length;
	}

	var row = table.insertRow(index);

	//row.setAttribute("name", row_name);
	row.setAttribute("name", "row_" + address);
	row.setAttribute("id", "flat_view_row_" + address);
	
//	row.setAttribute("tabindex", "0");
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


	instruction_args.innerHTML = parse(new_code, code[2]);
	instruction_args.setAttribute("id", "instruction_args");
	instruction_args.setAttribute("contenteditable", "true");

	//input_code_cell.setAttribute("value", code.join("\t"));
	//input_code_cell.setAttribute("readonly", "true");

	code_cell.id = "code_cell";
	code_cell.innerHTML = instruction.outerHTML + instruction_args.outerHTML;

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


function create_view(msg){
	var table = document.getElementById("flat_view_table");
	if(table.rows.length == 1){
		var row_name = undefined;
		var section_size = Object.keys(msg);
		for(var i = 0; i < section_size.length; i++){
			var section_index = section_size[i];
			var section_name = msg[section_size[i]][0];
			
			var section_code = msg[section_size[i]][1];
			var section_addreses = Object.keys(section_code);
//			console.log(section_code);
		
			create_table_row(section_name, section_name, undefined, undefined, -1);
			for(var j = 0; j < section_addreses.length; j++){
				create_table_row(section_name, undefined, section_addreses[j], section_code[section_addreses[j]], -1);	
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









