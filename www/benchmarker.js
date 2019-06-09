var time_function = {

};


/*
	so much code is slow	
		https://hackernoon.com/how-to-make-your-javascript-code-faster-8989869d41af


*/


/*

		-	Yes. I know about the dev tools ....  
			-	benchmark is for something else!

			-	and dev tools are messy. They used to be good.

		-	this is useful....
*/

function start_function(name){
	if(benchmark == true){
		if(time_function.hasOwnProperty(name)){
			time_function[name][0] = Date.now();
		}else{
			time_function[name] = [Date.now(), 0];
		}
	}
}

function end_function(name){
	if(benchmark == true){
		if(time_function.hasOwnProperty(name)){
			var delta = (Date.now() - time_function[name][0])/1000;
			time_function[name][1] += delta;	
		}else{
			console.log("forgot to start_function?");
		}
	}
}

function show_log(){
	for(key in time_function){
		console.log(key);
		console.log(time_function[key][1]);
		console.log("");
	}
}







