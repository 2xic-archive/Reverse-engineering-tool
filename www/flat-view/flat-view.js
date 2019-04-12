
var last_target = -1;

function create_table_row(row_name, section, address, code, index){
	var table = document.getElementById("myTable");
		
	if(index == -1){
		index = table.rows.length;
	}

	var row = table.insertRow(index);

	row.setAttribute("name", row_name);

	var section_cell = row.insertCell(0);

	if(section != undefined){
		section_cell.innerHTML = section;
	}

	if(address == undefined && code == undefined){
		return;
	}

	var address_cell = row.insertCell(1);
	address_cell.innerHTML = address;
	address_cell.id = "address_cell";


	var code_cell = row.insertCell(2);
	var input_code_cell = document.createElement("input");
	input_code_cell.setAttribute("value", code);
	input_code_cell.setAttribute("readonly", "true");

	code_cell.id = "code_cell";
	code_cell.innerHTML = input_code_cell.outerHTML;

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
		console.log("we out here");
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
	});
}


function create_view(msg){
	var table = document.getElementById("myTable");
	if(table.rows.length == 1){
		var row_name = undefined;
		for(var i = 0; i < msg.length; i++){
			if(msg[i].length == 1){
				row_name = msg[i][0];
				create_table_row(row_name, msg[i][0], undefined, undefined, -1);
			}else{
				create_table_row(row_name, undefined, msg[i][0], msg[i][1], -1);	
			}
		}
	}

	socket.on('size response', function( msg ) {
		//	note you should actually readjust evrey address .....
		// 	n_i = n_i-1 + size

		var prev_target_element = document.getElementById("myTable").rows[msg["target"] - 1];
		var next_address = parseInt(prev_target_element.children[1].innerHTML, 16) + msg["size"];

		var target_element = document.getElementById("myTable").rows[msg["target"]];
		target_element.children[1].innerHTML = "0x" + next_address.toString(16);
	});
}









