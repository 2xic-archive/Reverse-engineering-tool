
class tree_node {


	constructor(code_block, hirachy_level) {
		this.edges = [];
		this.direction = [];

		this.x = 0;
		this.y = 0;

		this.heigth = 1;
		this.width = 200;

		this.highest_node_heigth = 0;

		this.padding = 0;
		
		this.horizontal_gap = 220;
		this.vertical_gap = 200;

		this.code_block = code_block;
		this.is_root = false;

		this.hirachy_level = hirachy_level;
		this.adjusted_level = -1;

		this.draw();
		this.self_refrence = false;
	}

	debug(string){
		var debug = true;
		if(debug){
			console.log("[DEBUG]" + "[" + this.unqiue_id +"]" + string);
		}
	}

	get is_leaf() {
		return this.edges.length == 0;	
	}

	place(x, y){
		this.x = x;
		this.y = y;
	}

	connect_nodes(ctx, x0, y0, x1, y1, color) {
		ctx.beginPath();
		ctx.strokeStyle = color;
		ctx.moveTo(x0, y0);
		if(x0 == x1){
			ctx.quadraticCurveTo(x0 , y0, x1 , y1);
		}
		else if(x0 < x1){
			ctx.quadraticCurveTo(x0 + 50, y0, x1 , y1);
		}else{
			ctx.quadraticCurveTo(x0 - 50, y0, x1 , y1);
		}
	
		ctx.stroke();
	}

	connect_nodes_curve(ctx, x0, y0, x1, y1, weigth, color) {
		ctx.beginPath();
		ctx.moveTo(x0, y0);
		ctx.bezierCurveTo(x0 + this.width, y0 + this.heigth , x1 + this.width, y1 - this.heigth , x1, y1); 
		if(color == "black"){
			ctx.strokeStyle = "blue";
		}else{
			ctx.strokeStyle = color;	
		}
		ctx.stroke();
		ctx.strokeStyle = "black";
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

	get unqiue_id(){
		return this.code_block[0]["address"];
	}

	generate_table(){
		var code_table = document.createElement("table");
		var table_body = document.createElement("tbody");

		var table_id = "table" + this.unqiue_id;

		code_table.setAttribute("id", table_id);
		code_table.setAttribute("name", "grapth_table_code");
		code_table.setAttribute("tabindex", "0");

			
		for(var i = 0; i < this.code_block.length; i++){
			var row = table_body.insertRow(i);
			row.setAttribute("name", "row_" + this.code_block[i]["address"]);
			row.setAttribute("id", "grapth_" + this.code_block[i]["address"]);
			row.setAttribute("type", "grapth");

			var address_cell = row.insertCell(0);
			var instruction_cell = row.insertCell(1);
			var argument_cell = row.insertCell(2);

			address_cell.innerHTML = this.code_block[i]["address"];
			address_cell.id = "address_cell";

			instruction_cell.innerHTML = this.code_block[i]["instruction"];
			argument_cell.innerHTML = this.code_block[i]["argument"];

			if(this.code_block[i]["argument"][0] == "0" && this.code_block[i]["argument"][1] == "x"){
				argument_cell.setAttribute("onmouseover", "highlight(this)");
				argument_cell.setAttribute("onmouseout", "highlight_low(this)");
				argument_cell.setAttribute("onkeydown", "highlight(this)");
				argument_cell.setAttribute("onClick", "jump_2_node(this)");
			}
			row.setAttribute("onClick", "moving_rows(this)");
	
			table_body.appendChild(row);
		}

		code_table.appendChild(table_body);
		code_table.style.minWidth = "100%";
		return [code_table.outerHTML, table_id];
	}

	draw(){
		var element = document.getElementById(this.unqiue_id);
		if(element == undefined){
			var node_div = document.createElement("div");

			node_div.setAttribute("level", this.hirachy_level);
			node_div.setAttribute("class", "nodes");
			node_div.setAttribute("id", this.unqiue_id);
				
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
			this.width = document.getElementById(table[1]).offsetWidth;
			node_div.style.minHeight = this.heigth + "px";
			node_div.style.maxHeight = this.heigth + "px";

			
			this.element_reference = document.getElementById(this.unqiue_id);
			this.table_reference  = document.getElementById("table" + this.unqiue_id);

		}else{
			element.style.top = this.node_top + "px";
			element.style.left = this.node_left + "px";
			this.element_reference = element;
		}


		if(this.is_root){
			this.element_reference.setAttribute("root", "yes");
		}

//		this.debug( this.node_top + "	"  +  this.node_left);		
	}

	enable_self_refrence(){
		this.self_refrence = true;
	}

	padding_nodes(){
		var padding = 0;
		var rightmost = new Array(this.edges.length);
		var highest_heigth = 0;
		

		if(this.edges.length == 2 && this.self_refrence){
			padding = 0;
		//	this.debug("1");
		}else if(this.edges.length == 1){
			padding = 0;
		//	this.debug("1");
		}else{
			padding = - this.width;
		//	this.debug("2");
		}

		for (var i = 0; i < this.edges.length; i++) {
			if(this.unqiue_id  == this.edges[i].unqiue_id){
				continue;
			}

			if(highest_heigth < this.edges[i].heigth){
				highest_heigth = this.edges[i].heigth;
			}
			
			if(!(this.edges[i].adjusted_level < this.hirachy_level) || this.edges[i].adjusted_level == -1){		
				this.edges[i].padding = padding;	
			}
			padding += this.horizontal_gap + this.edges[i].width;
		}

		this.highest_heigth = highest_heigth;
		return padding;
	}

	
	adjust_nodes(padding){
		for (var i = 0; i < this.edges.length; i++){
			if(this.unqiue_id  == this.edges[i].unqiue_id){
				continue;
			}
			if(!(this.edges[i].adjusted_level < this.hirachy_level) || this.edges[i].adjusted_level == -1){
				this.edges[i].adjusted_level = this.hirachy_level;
			}else{
				continue;
			}
			this.edges[i].padding -= this.edges[i].padding * 0.5;
		//	this.debug("Setting -> "+ this.edges[i].unqiue_id + "	to " + this.edges[i].padding)
		}
	}

	position_edges(){
		this.padding_nodes();
		this.adjust_nodes();			
	}

	add_edge(node, direction){
		if(this.edges.indexOf(node) == -1){
			this.edges.push(node);
			this.direction.push(direction);
		}
	}
}

