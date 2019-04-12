
class tree_node {
	constructor(content, head_positon) {
		this.edges = [];
		this.direction = [];

		this.x = 0;
		this.y = 0;

		this.heigth = content.split("<br>").length * 15;
		this.width = 200;

		this.largest_padding = 0;
		this.highest_node_heigth = 0;

		this.padding = 0;
		this.head_positon = head_positon;

		this.horizontal_gap = 220;
		this.vertical_gap = 100;

		this.content = content;
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
		return this.content.hashCode();
	}


	draw(){
		var element = document.getElementById(this.gethash.toString());
		if(element == undefined){
			var node_div = document.createElement("div");
			node_div.setAttribute("class", "nodes");
			node_div.setAttribute("id", this.gethash.toString());
				
			node_div.style.top = this.node_top+ 'px';
			node_div.style.left = this.node_left+ 'px';
				
			node_div.style.minHeight = this.heigth  + 'px';
			node_div.style.minWidth = this.width+ 'px';

			node_div.style.maxHeight = this.heigth  + 'px';
			node_div.style.maxWidth = this.width+ 'px';			
				
			node_div.innerHTML = this.content;
			//; +'		[' + this.node_left + "	" + this.node_top + ']' +'		[' + this.node_top + "	" + this.node_left + ']';
			document.getElementById("grapth").appendChild(node_div);

			this.element_refrence = document.getElementById(this.content.hashCode().toString());
		}else{
			element.style.top = this.node_top+ 'px';
			element.style.left = this.node_left+ 'px';

			this.element_refrence = element;

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

