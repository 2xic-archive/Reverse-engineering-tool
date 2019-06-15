

var element_history = [];
var future_histroy = [];



Array.prototype.peek = function(el){
	if(this.length > 0){
		return this[this.length-1];
	}else{
		return undefined;
	}
};

function interact_with_target(target){
	target.focus();
	target.scrollIntoView();
	target.click();
}

function rewind(){
	var future = document.getElementById("contentArea").rows[global_row_index];
	add_element_future(future);
	
	var past = element_history.pop();
	interact_with_target(past);

	if(element_history.length == 0){
		document.getElementById("backward").disabled = true;
	}
}

function forward(){
	add_element_history(document.getElementById("contentArea").rows[global_row_index], true);	

	var future = future_histroy.pop();
	interact_with_target(future);

	if(future_histroy.length == 0){
		document.getElementById("forward").disabled = true;
	}
}

function add_element_history(element, from_forward){
	if(element_history.length == 0 || element_history[element_history.length - 1] != element){
		element_history.push(element);
	}

	if(!from_forward){
		// future is changed
		future_histroy = [];
		document.getElementById("forward").disabled = true;
	}

	if(element_history.length == 1){
		document.getElementById("backward").disabled = false;
		document.getElementById("backward").onclick = rewind;
	}
}

function add_element_future(past){
	if(future_histroy[future_histroy.length - 1] != past){
		future_histroy.push(past);
	}
	if(future_histroy.length == 1){
		document.getElementById("forward").disabled = false;
		document.getElementById("forward").onclick = forward;
	}
}


