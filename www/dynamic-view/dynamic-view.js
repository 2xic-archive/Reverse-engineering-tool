



/*
	basic dynamic view
*/
var dynamic_data = undefined;
function re_draw_table(index){
/*	for(var i = 0; i < data[register_hits[0]].length + 1; i++){
		var count_option = document.createElement("option");
		count_option.setAttribute("value", i);
		count_option.innerHTML = "Address trace number " + i;
		trace_list.appendChild(count_option);
	}
*/
	for(var i = 0, row_number = 0; i < register_hits.length; row_number++){		
		var row = register_table.rows[row_number];
		for(var j = 0; j < 4 && i < register_hits.length; j+=2, i++){
/*
			var register_cell = row.insertCell(j);
			register_cell.innerHTML = register_hits[i];
			register_cell.id = "register_cell";
*/
			var register_value_cell = row.insertCell(j + 1);
			register_value_cell.innerHTML = "0x" + dynamic_data[register_hits[i]][index].toString(16);
			register_value_cell.id = register_hits[i] + "_value";
		}
	}
}

function create_dynamic_view(data){
	//var container = document.createElement("div");
	var register_table = document.createElement("table");
	var trace_list = document.createElement("select");
	trace_list.id = "trace_list";

	trace_list.style.width = "100%";


	dynamic_data = data;
	
	trace_list.onchange = function(){
		var i = document.getElementById("trace_list").value;
		re_draw_table(i);
	};

	/*container.style.height = "100%";
	container.style.minHeight = "100%";

	container.style.borderLeft = "solid";
	*/


	var container = document.getElementsByName("dynamic_div")[0];
	var register_hits = Object.keys(data);	
	//console.log(data);
	if(register_hits == 0){
		container.innerHTML = `<center>
							<h1>no dynamic data available</h1>						
						</center>`;
	}else{	
		// the length will be the same for all reigsters...

		for(var i = 0; i < data[register_hits[0]].length + 1; i++){
			var count_option = document.createElement("option");
			count_option.setAttribute("value", i);
			count_option.innerHTML = "Address trace number " + i;
			trace_list.appendChild(count_option);
		}

		for(var i = 0, row_number = 0; i < register_hits.length; row_number++){
			
			var row = register_table.insertRow(row_number);
			for(var j = 0; j < 4 && i < register_hits.length; j+=2, i++){
				var register_cell = row.insertCell(j);
				register_cell.innerHTML = register_hits[i];
				register_cell.id = "register_cell";


				var register_value_cell = row.insertCell(j + 1);
				register_value_cell.innerHTML = "0x" + data[register_hits[i]][0].toString(16);
				register_value_cell.id = register_hits[i] + "_value";
			}
		}
		container.style.backgroundColor = "#C0C0C0";
		container.style.borderLeft = "solid";

		container.innerHTML = trace_list.outerHTML + register_table.outerHTML;
	}
}





