


class highlighter {
	constructor(){
		this.last_highighlight = undefined;
	}

	highligth(target){
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

function code_highlighter(current, registers){
	var current_text = current;
	if(registers.length == 0){
		registers.push("none");
	}

	for(var i = 0; i < registers.length; i++){
		var word_length = registers[i].length;
		var word = registers[i];
		var key_word_index = 0;
		
		var refrence_count = 0;
		var searching = true;

		var j = 0;
		var size = current_text.length;

		var hex_mode = false;
		var hex_start = 0;

		if(word != "none"){
			all_registers.add(word);
		}
		
		while(j < size){
			if(current_text[j] == "<"){
				refrence_count += 1;
			}
			if(current_text[j] == ">"){
				refrence_count -= 1;
			}

			if(current_text[j] == "0"){
				if((j + 1) < size){
					if(current_text[j + 1] == "x"){
						hex_mode = true;
						hex_start = j;
					}
				}
			}

			if(word[key_word_index] == current_text[j] && searching && refrence_count == 0){
				key_word_index += 1;
				if(key_word_index == word_length){
					if(refrence_count == 0){
						var span_end = "</span>";
						var span_start = "<span style='color:red;' contenteditable='true' key='" + word +"'>";
						current_text = current_text.insert(j + 1, span_end);
						current_text = current_text.insert(j - word_length + 1, span_start);

						size += span_start.length + span_end.length;
						j += (span_start.length + span_end.length);// + 1;
					}else{
						console.log("hm");
					}
				}
			}else{
				key_word_index = 0;
				searching = false;
			}

			if(current_text[j] == " " || current_text[j] == "[" || current_text[j] == "]" || current_text[j] == ","){
				searching = true;
				if(hex_mode){
					var span_end = "</span>";
					var span_start = "<span style='color:blue;' key='" + "hex" +"'>";
					current_text = current_text.insert(j, span_end);
					current_text = current_text.insert(hex_start, span_start);

					size += span_start.length + span_end.length;
					j += (span_start.length + span_end.length);// 		
					hex_mode = false;
				}
			}
			j++;
		}
		if(hex_mode){
			var span_end = "</span>";
			var span_start = "<span style='color:blue;' key='" + "hex" +"'>";
			current_text = current_text.insert(j, span_end);
			current_text = current_text.insert(hex_start, span_start);

			size += span_start.length + span_end.length;
			j += (span_start.length + span_end.length);// 		
			hex_mode = false;
		}
	}
	return current_text;
}