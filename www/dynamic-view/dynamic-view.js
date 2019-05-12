



/*
	basic dynamic view
*/
function create_dynamic_view(data){
	var container = document.createElement("div");
	var register_table = document.createElement("table");
	var hit_count = document.createElement("select");

	hit_count.style.width = "100%";
	container.style.height = "100%";
	container.style.minHeight = "100%";

	container.style.borderLeft = "solid";

	for(var i = 0; i < data.length; i++){
		var count_option = document.createElement("option");
		count_option.setAttribute("value", i);
		count_option.innerHTML = "adress hit number " + i;
		hit_count.appendChild(count_option);
	}

	if(data.length == 0){
		document.getElementsByName("dynamic-div")[0].innerHTML = `<center>
							<h1>no dynamic data available</h1>						
						</center>`;
	}else{
		var register_hits = Object.keys(data[0]);	
		for(var i = 0, row_number = 0; i < register_hits.length; row_number++){
			var row = register_table.insertRow(row_number);
			for(var j = 0; j < 4 && i < register_hits.length; j+=2, i++){
				var register_cell = row.insertCell(j);
				register_cell.innerHTML = register_hits[i];
				register_cell.id = "register_cell";


				var register_value_cell = row.insertCell(j + 1);
				register_value_cell.innerHTML = data[0][register_hits[i]];
				register_value_cell.id = register_hits[i] + "_value";
			}
		}
		container.innerHTML = hit_count.outerHTML + register_table.outerHTML;

		document.getElementsByName("dynamic-div")[0].innerHTML = container.outerHTML;
	}
}





