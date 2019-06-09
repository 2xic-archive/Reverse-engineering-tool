


var hex_ligther = new highlighter(); 


var insert_text = "<span style='color:red'>";
var end_text = "</span>";


String.prototype.hex_show = function (start, end) {
	end += (((end - start) ) * 2);
	if (0 < start){
		return this.substring(0, start) + insert_text + this.substring(start, end) + end_text + this.substring(end, this.length);
	}else if(start == 0){
		return insert_text + this.substring(start, end) + end_text + this.substring(end, this.length);	
	}
};
		
String.prototype.hex_hide = function (start, end) {
	end += (((end - start) ) * 2);			
	if (0 < start ){
		var delta = start + insert_text.length;
		var delta_end = delta + end;
//		console.log(this.substring(delta + end, this.length));
		return this.substring(0, start) + this.substring(delta, delta + end) + this.substring(delta_end, this.length);
	} else if(start == 0){
		var delta = insert_text.length + end;
		return this.substring(insert_text.length, delta) + this.substring(delta + end_text.length, this.length);
	}
};


function resolve(e){
	var name = e.getAttribute("name");
	var targets = document.getElementsByName(name);
	hex_ligther.highlight(targets);	
}
//	basic hex view
function create_hex_view(hex){


/*	var hex_table = document.getElementById("hex_table");
	hex_table.id = "hex_table";
	hex_table.setAttribute("name", "hex_table");
	*/
	var data = [];
	for(var i = 0, j = 0; i < hex.length; i += 16, j++){
		var row = document.createElement("tr");
		var span = document.createElement("span");
		
		for(var q = 0; q < 16; q++){
			if(i + q < hex.length){
			/*	var table_data = document.createElement("td");
			//	table_data.setAttribute("onClick", "resolve(this)");
				table_data.innerHTML = hex[i + q];
			//	table_data.setAttribute("name", i + q); 
				row.appendChild(table_data);
				*/
				span.innerText += hex[i + q] + " ";// + " ";
			}
		}
		row.appendChild(span);
		data.push(row.outerHTML);
	}
	

	//var clusterize = 
	new Clusterize({
		rows: data,
		scrollId: 'hex_scroll',
		contentId: 'hex_area',
		blocks_in_cluster:100
	});



	//var char_table = document.getElementById("char_table");
	var char_data = [];
	for(var i = 0, j = 0; i < hex.length; i += 16, j++){
		var row = document.createElement("tr");
		var td = document.createElement("td");
		var span = document.createElement("span");
		//for(var q = 0; q < data[i].children.length; q++){
		for(var q = 0; q < 16; q++){
			/*span.setAttribute("name", (i * 16) + q); 
			span.setAttribute("onClick", "resolve(this)");
					//= (i * 8) + q;
			var hex_2_intenger = parseInt(hex_table.rows[i].children[q].innerHTML, 16);
			if(hex_2_intenger == 0){
				span.innerHTML = "&nbsp;";		
			}else{
				span.innerHTML = String.fromCharCode(hex_2_intenger);
			}*/
			if(i + q < hex.length){
				var hex_2_intenger = parseInt(hex[i + q], 16);
				if(hex_2_intenger == 0){
					span.innerText += " ";		
				}else{
					span.innerText += String.fromCharCode(hex_2_intenger);
				}
			}
		}
		td.appendChild(span);
		row.appendChild(td);
		char_data.push(row.outerHTML);
	}
	//var clusterize = 
	new Clusterize({
		rows: char_data,
		scrollId: 'char_scroll',
		contentId: 'char_area',
		blocks_in_cluster:100
	});





	console.log("done");
}