


class highlighter {
	constructor(){
		this.last_highighlight = undefined;
	}

	highlight(target){
		if(this.last_highighlight != undefined){
			for(var i = 0; i < this.last_highighlight.length; i++){
				this.last_highighlight[i].style.background = "";
			}
		}
		for(var i = 0; i < target.length; i++){
			target[i].style.backgroundColor = "rgba(255, 255, 255, 0.7)";
		}
		this.last_highighlight = target;
	}
}

String.prototype.insert = function (index, string) {
	if (index > 0){
		return this.substring(0, index) + string + this.substring(index, this.length);
	}
	return string + this;
};

function stop_char(char){
	if(char == "\t" || char == " " || char == "[" || char == "]" || char == ","){
		return true;
	}
	return false;
}

function code_highlighter(current, registers, target){
	var current_text = current;
	if(registers.length == 0){
		registers.push("none");
	}

	var insertions = 0;
	var possible_splits = current.split(" ").length;

	for(var i = 0; i < registers.length && (insertions < possible_splits); i++){
		var word_length = registers[i].length;

		var word = registers[i];
		var key_word_index = 0;
		
		var refrence_count = 0;
		var searching = true;

		var index = 0;
		var size = current_text.length;

		var hex_mode = false;
		var hex_start = 0;
		var space_since_stop = 0;

		if(word != "none"){
			all_registers.add(word);
		}
		
		while(index < size && (insertions < possible_splits)){
			if(current_text[index] == "<"){
				refrence_count += 1;
			}
			if(current_text[index] == ">"){
				refrence_count -= 1;
			}

			if(current_text[index] == "0"){
				if((index + 1) < size){
					if(current_text[index + 1] == "x"){
						hex_mode = true;
						hex_start = index;
					}
				}
			}

			if(space_since_stop == 0 && !hex_mode && !isNaN(current_text[index]) && !stop_char(current_text[index]) && refrence_count == 0){
				hex_mode = true;
				hex_start = index;
			}

			if(word[key_word_index] == current_text[index] && searching && refrence_count == 0){
				key_word_index += 1;
				if(key_word_index == word_length){
					if(refrence_count == 0){
						var span_end = "</span>";
						var span_start = "<span style='color:red;' contenteditable='false' key='" + word +"'>";
						current_text = current_text.insert(index + 1, span_end);
						current_text = current_text.insert(index - word_length + 1, span_start);
						insertions++;

						size += span_start.length + span_end.length;
						index += (span_start.length + span_end.length);// + 1;
					}else{
						console.log("hm");
					}
				}
			}else{
				key_word_index = 0;
				searching = false;
			}

			if(stop_char(current_text[index])){
				searching = true;
				if(hex_mode){
					var span_end = "</span>";
					var span_start = "<span style='color:blue;' key='" + "hex" +"'>";
					current_text = current_text.insert(index, span_end);
					current_text = current_text.insert(hex_start, span_start);
					insertions++;

					size += span_start.length + span_end.length;
					index += (span_start.length + span_end.length);// 		
					hex_mode = false;
				}
				space_since_stop = 0;
			}else{
				space_since_stop += 1;
			}
			index++;
		}
		if(hex_mode){
			var span_end = "</span>";
			var span_start = "<span style='color:blue;' key='" + "hex" +"'>";
			current_text = current_text.insert(index, span_end);
			current_text = current_text.insert(hex_start, span_start);

			size += span_start.length + span_end.length;
			index += (span_start.length + span_end.length);// 		
			hex_mode = false;
		}
	}
	if(target == undefined){
		return current_text;
	}else{
		worker.postMessage({
			'cmd': 'code_highlighter', 
			'value': current_text
		});
	}
}

//console.log(code_highlighter("add	rsp, 8", []));



