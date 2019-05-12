


var hex_ligther = new highlighter(); 

function resolve(e){
	var name = e.getAttribute("name");
	var targets = document.getElementsByName(name);
	hex_ligther.highlight(targets);	
}
//	basic hex view
function create_hex_view(hex){
	var hex_table = document.getElementById("hex_table");
	hex_table.id = "hex_table";
	hex_table.setAttribute("name", "hex_table");
	for(var i = 0, j = 0; i < hex.length; i += 16, j++){
		var row = hex_table.insertRow(j);
		for(var q = 0; q < 16; q++){
			if(i + q < hex.length){
				var table_data = document.createElement("td");
				table_data.setAttribute("onClick", "resolve(this)");
				table_data.innerHTML = hex[i + q];
				table_data.setAttribute("name", i + q); 
				row.appendChild(table_data);
			}
		}
	}

	var char_table = document.getElementById("char_table");
	for(var i = 0; i < hex_table.rows.length; i++){
		var row = char_table.insertRow(i);
		for(var q = 0; q < hex_table.rows[i].children.length; q++){
			var table_data = document.createElement("td");
			table_data.setAttribute("name", (i * 16) + q); 
			table_data.setAttribute("onClick", "resolve(this)");
					//= (i * 8) + q;
			var hex_2_intenger = parseInt(hex_table.rows[i].children[q].innerHTML, 16);
			if(hex_2_intenger == 0){
				table_data.innerHTML = "&nbsp;";		
			}else{
				table_data.innerHTML = String.fromCharCode(hex_2_intenger);
			}
			row.appendChild(table_data);
		}
	}
}