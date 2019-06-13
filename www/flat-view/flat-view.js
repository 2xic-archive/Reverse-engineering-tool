
var last_target = -1;
var look_up_row = {

};
var all_registers = new Set([]);
var current_section = undefined;


var code_comments = {

}

var code_sections = {

}

var section_size = {

}

var table = undefined;


/*
var worker = new Worker('flat-view-worker.js');
worker.onmessage = function(e) {
	console.log(e);
};

worker.onerror = function(e) {
	console.log(e);
//	alert('Error: Line ' + e.lineno + ' in ' + e.filename + ': ' + e.message);
};*/


function init_section(section, index){
	//var table = document.getElementById("flat_view_table");
	var row = document.createElement("tr");

	row.setAttribute("name", "row_" + section);
	row.setAttribute("onClick", "moving_rows(this)");
	row.setAttribute("type", "flat");


	var adress_cell = document.createElement("td");;
	adress_cell.innerHTML = section;
	current_section = section;
	row.setAttribute("id", "section");
	row.setAttribute("section", current_section);
	row.appendChild(adress_cell);
	return row.outerHTML;
}

function create_table_row(section, address, code, size){
	var row = document.createElement("tr");
	row.setAttribute("name", address);
	//row.setAttribute("onClick", "moving_rows(this)");

	//table.insertRow(-1);

	//row.id = "flat_view_row_" + address;

	//.setAttribute("id", "flat_view_row_" + address);
//	row.setAttribute("onClick", "moving_rows(this)");
//	row.setAttribute("name", address);

//	row.setAttribute("type", "flat");
	row.setAttribute("section", current_section);
/*	row.setAttribute("name", "row_" + address);
*/

//	var section_cell = row.insertCell(0);
	
	// I was told that generating objects by using string
	// is faster. That is a lie. I have tested....
	var address_cell = document.createElement("td"); //row.insertCell(0);
	address_cell.innerText = address;
	address_cell.id = "address_cell";



	var code_cell = document.createElement("td");
	code_cell.innerHTML = code["instruction"] + "\t" + code_highlighter(code["argument"], code["registers"])
//	code_cell.id = "comment_cell_" + address;


/*
	worker.postMessage({
		"cmd": 'code_highlighter', 
		"text": code["argument"], 
		"register":code["registers"],
		"target":("comment_cell_" + address)
	});
*/

	var comment_cell = document.createElement("td");
	comment_cell.setAttribute("comment", "");
	var comment = code["comment"];
	if(comment != undefined){
		comment_cell.innerText = comment;
	}
	//	this is so much faster than insertcell/insertrow.
	//	javascript need better datastuctures !
	row.appendChild(address_cell);
	row.appendChild(code_cell);
	row.appendChild(comment_cell);
//	table.tBodies[0].appendChild(row);

	row.setAttribute("size", (size[1]-size[0]));

	return row.outerHTML;
//	var code_content = document.createElement("span");


//	code_cell.innerText = code["instruction"];// + "\t" + code_highlighter(code["argument"], code["registers"]);

		/*

	start_function("code_highlighter");
	code_content.innerHTML = code["instruction"];// + "\t" + code_highlighter(code["argument"], code["registers"]);
	end_function("code_highlighter");

	//	basic parsing of target
	if(code["argument"][0] == "0" && code["argument"][1] == "x"){
		code_content.setAttribute("ondblclick", "find_node(this)");
		code_content.setAttribute("jmp_target", code["argument"]);
	}

	code_cell.innerHTML = code_content.outerHTML;
	code_cell.id = "code_cell";
	*/





	// comment cell
/*	if(code.hasOwnProperty("comment")){
		var comment_cell = row.insertCell(3);
	}
*/

/*	comment_cell.id = "comment";
	var span_comment = document.createElement("span");
	
	span_comment.innerText = code["comment"];
	comment_cell.innerHTML = span_comment.outerHTML;
*/

//	row.setAttribute("end", size[1]);

}

function create_flat_view(msg){
//	table = document.getElementById("flat_view_table");
//	table.setAttribute("tabindex", "0");
	
	var data = [];
	
	//return new Promise(resolve => {
	//	var section_size = Object.keys(msg);
		
		//for(var i = 0; i < section_size.length; i++){
		for(section_index in msg){
			//	this is the section
		
		//	var section_index = section_size[i];
			var section_name = msg[section_index]["section_name"];

			//	check if it is already created
			if(document.getElementsByName("row_" + section_name).length > 0){
				continue;
			}


			
			var section_code = msg[section_index]["code"];
			var section_addreses = Object.keys(section_code);
			
			start_function("section_init");
			data.push(init_section(section_name, -1));
		//	current_index++;
			end_function("section_init");

			start_function("row_generator");
			var instruction_position = 0;
			var padding = code_sections[section_name][0];
			var j = 0;
			console.log(section_addreses.length);
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
				data.push(create_table_row(section_name, section_addreses[address_index], section_code[address], size));
				//	0.21700000000000003
				instruction_position += instruction_size;
	/*			if(10000 < j){
					break;
				}
				j++;*/
			}
			end_function("row_generator");
		}

	return data;
}


/*
socket.on('size response', function( msg ) {
		//	note: you should actually readjust every address .....
	// 	n_i = n_i-1 + size

	var prev_target_element = document.getElementById("flat_view_table").rows[msg["target"] - 1];
	var next_address = parseInt(prev_target_element.children[1].innerHTML, 16) + msg["size"];

	var target_element = document.getElementById("flat_view_table").rows[msg["target"]];
	target_element.children[1].innerHTML = "0x" + next_address.toString(16);
});
*/





