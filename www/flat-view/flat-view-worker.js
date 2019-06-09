

self.onmessage = function(e) {
	if(e.data.cmd == "code_highlighter"){
		code_highlighter(e.data.text, e.data.register, e.data.target);
	}
	//console.log(e);
	//CalculatePi(e.data.value);
}


/*
worker.postMessage({
	'cmd': 'CalculatePi', 
	'value': [document.getElementById("loop").value, 100]
});
*/