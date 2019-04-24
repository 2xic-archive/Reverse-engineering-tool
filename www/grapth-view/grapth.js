
class tree_node {
	constructor(code_block, head_positon) {
		this.edges = [];
		this.direction = [];

		this.x = 0;
		this.y = 0;

		this.heigth = 1;
		this.width = 200;

		this.largest_padding = 0;
		this.highest_node_heigth = 0;

		this.padding = 0;
		this.head_positon = head_positon;

		this.horizontal_gap = 220;
		this.vertical_gap = 100;

		this.code_block = code_block;
		this.is_root = false;
		this.draw();
	}

	get is_leaf() {
		return this.edges.length == 0;	
	}

	place(x, y){
		this.x = x;
		this.y = y;
	}

	connect_nodes(ctx, x0, y0, x1, y1) {
		ctx.beginPath();
		ctx.moveTo(x0, y0);
		ctx.lineTo(x1, y1);
		ctx.stroke();
	}

	get node_left(){
		return this.x - (this.width) / 2;
	}

	get node_top(){
		if(this.highest_node_heigth == 0){
			return this.y - (this.heigth) / 2;
		}else{
			return this.y - (this.highest_node_heigth) / 2;
		}
	}
		
	get node_half_top(){

		return 0.5 * this.heigth;
	}

	get node_half_left(){
		return 0.5 * this.width;
	}

	get gethash(){
		// basic hash function	(will change)
		//	https://stackoverflow.com/questions/7616461/generate-a-hash-from-string-in-javascript
		String.prototype.hashCode = function() {
			var hash = 0;
			if (this.length == 0) {
				return hash;
			}
			for (var i = 0; i < this.length; i++) {
				var char = this.charCodeAt(i);
				hash = ((hash<<5)-hash)+char;
				hash = hash & hash; // Convert to 32bit integer
			}
			return hash;
		}
		var full_code = "";
		for(var i = 0; i < this.code_block.length; i++){
			full_code += this.code_block[i]["address"];
		}
		return full_code.hashCode();
	}

	generate_table(){
		var code_table = document.createElement("table");
		var table_body = document.createElement("tbody");

		var table_id = "table" + this.gethash;

		code_table.setAttribute("id", table_id);
		code_table.setAttribute("name", "grapth_table_code");

		for(var i = 0; i < this.code_block.length; i++){
			var row = table_body.insertRow(i);
			row.setAttribute("name", "row_" + this.code_block[i]["address"]);
			row.setAttribute("type", "grapth");

			var address_cell = row.insertCell(0);
			var instruction_cell = row.insertCell(1);
			var argument_cell = row.insertCell(2);

			address_cell.innerHTML = this.code_block[i]["address"];
			address_cell.id = "address_cell";

			instruction_cell.innerHTML = this.code_block[i]["instruction"];
			argument_cell.innerHTML = this.code_block[i]["argument"];

			table_body.appendChild(row);
		}
		code_table.appendChild(table_body);
		code_table.style.minWidth = "100%";
		return [code_table.outerHTML, table_id];
	}

	draw(){
		var element = document.getElementById(this.gethash.toString());
		if(element == undefined){
			var node_div = document.createElement("div");
			node_div.setAttribute("class", "nodes");
			node_div.setAttribute("id", this.gethash.toString());
				
			node_div.style.top = this.node_top + "px";
			node_div.style.left = this.node_left + "px";
				
			node_div.style.minHeight = this.heigth + "px";
			node_div.style.minWidth = this.width + "px";

			node_div.style.maxHeight = this.heigth  + "px";
			node_div.style.maxWidth = this.width + "px";			
			
			var table = this.generate_table(this.code_block);
			node_div.innerHTML = table[0];

			document.getElementById("grapth").appendChild(node_div);

			//	finding the actual heigth and readjusting the node size 
			this.heigth = document.getElementById(table[1]).offsetHeight;
			this.width = document.getElementById(table[1]).offsetWidth + 30;
			node_div.style.minHeight = this.heigth + "px";
			node_div.style.maxHeight = this.heigth + "px";

		//	node_div.style.minWidth = this.width + "px";
		//	node_div.style.maxWidth = this.width + "px";			
			
			this.element_reference = document.getElementById(this.gethash.toString());
		}else{
			element.style.top = this.node_top + "px";
			element.style.left = this.node_left + "px";
			this.element_reference = element;
		}
	}

	padding_nodes(){

		var padding = 0;
		var rightmost = new Array(this.edges.length);
		var highest_heigth = 0;

		for (var i = 0; i < this.edges.length; i++) {
			if(i > 0){
				for (var j = 0; j < this.edges.length; j++){
					padding = Math.max(padding, rightmost[j] + this.horizontal_gap);
					if(highest_heigth < this.edges[j].heigth){
						highest_heigth = this.edges[j].heigth;
					}
				}
			}
			for (var j = 0; j < this.edges.length; j++){
				rightmost[j] = padding;	
				if(this.largest_padding < padding){
					this.largest_padding = padding;
				}
				this.edges[j].highest_node_heigth = highest_heigth;
			}
			this.edges[i].padding = padding;
		}
		return padding;
	}
	
	adjust_nodes(padding){
		for (var i = 0; i < this.edges.length; i++){
			this.edges[i].padding -= 0.5 * padding
		}
	}

	position_edges(){
		this.adjust_nodes(this.padding_nodes());			
	}

	add_edge(node, direction){
		if(this.edges.indexOf(node) == -1){
			this.edges.push(node);
			this.direction.push(direction);
		}
	}
}

